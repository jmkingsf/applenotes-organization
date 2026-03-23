"""Semantic search and indexing operations using FAISS + paraphrase-MiniLM."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from . import faiss_store
from .note_operations import NoteOperations, NoteDetails

_LOGGER = logging.getLogger(__name__)

_model_lock = threading.Lock()
_model_instance: Optional[SentenceTransformer] = None

_index_lock = threading.Lock()


def _get_model() -> SentenceTransformer:
    global _model_instance
    if _model_instance is None:
        with _model_lock:
            if _model_instance is None:
                _LOGGER.info(f"Loading model: {faiss_store._MODEL_NAME}")
                _model_instance = SentenceTransformer(faiss_store._MODEL_NAME)
    return _model_instance


@dataclass(frozen=True)
class VectorSearchResult:
    """Result for a semantic search query."""

    name: str
    folder: str
    note_id: str
    distance: float  # cosine similarity — higher is more similar


class VectorSearch:
    """Semantic search operations backed by FAISS."""

    @staticmethod
    def index_folder(folder_name: str) -> int:
        """Index all notes in a folder. Returns the number of notes newly indexed."""
        notes = NoteOperations.list_notes_in_folder(folder_name)
        if not notes:
            _LOGGER.warning(f"No notes found in folder: {folder_name}")
            return 0
        return VectorSearch._index_note_list(notes, folder_name)

    @staticmethod
    def index_folder_first_n(folder_name: str, n: int) -> int:
        """Index the first N notes in a folder. Returns the number newly indexed."""
        notes = NoteOperations.list_notes_in_folder(folder_name)
        if not notes:
            _LOGGER.warning(f"No notes found in folder: {folder_name}")
            return 0
        return VectorSearch._index_note_list(notes[:n], folder_name)

    @staticmethod
    def index_note(note_name: str, folder_name: Optional[str] = None) -> bool:
        """Index a single note. Returns True if the note was (re)indexed."""
        with _index_lock:
            model = _get_model()
            index, metadata = faiss_store.load()
            try:
                note_details = NoteOperations.get_note_details(note_name, folder_name=folder_name)
            except Exception as e:
                _LOGGER.error(f"Could not fetch note '{note_name}': {e}")
                return False

            changed = VectorSearch._upsert_note(index, metadata, model, note_details)
            index, metadata = faiss_store.compact_if_needed(index, metadata, model)
            faiss_store.save(index, metadata)
            return changed

    @staticmethod
    def reindex_note(note_name: str, folder_name: Optional[str] = None) -> bool:
        """Force reindex a single note regardless of modification time. Returns True on success."""
        with _index_lock:
            model = _get_model()
            index, metadata = faiss_store.load()
            try:
                note_details = NoteOperations.get_note_details(note_name, folder_name=folder_name)
            except Exception as e:
                _LOGGER.error(f"Could not fetch note '{note_name}': {e}")
                return False

            note_id = note_details["note_id"]
            # Tombstone the old entry if present so we always re-encode.
            if note_id in metadata["note_id_to_faiss_id"]:
                old_fid = metadata["note_id_to_faiss_id"].pop(note_id)
                faiss_store.tombstone(metadata, old_fid)

            VectorSearch._upsert_note(index, metadata, model, note_details, force=True)
            index, metadata = faiss_store.compact_if_needed(index, metadata, model)
            faiss_store.save(index, metadata)
            return True

    @staticmethod
    def purge_index() -> None:
        """Clear the entire FAISS index and metadata."""
        with _index_lock:
            faiss_store.purge()

    @staticmethod
    def search(
        query: str,
        limit: int = 5,
        folder_name: Optional[str] = None,
    ) -> List[VectorSearchResult]:
        """
        Search indexed notes by cosine similarity.

        Args:
            query: Natural language search query
            limit: Max results to return
            folder_name: Optional folder to scope results

        Returns:
            List of VectorSearchResult sorted by descending similarity.
        """
        with _index_lock:
            model = _get_model()
            index, metadata = faiss_store.load()

        live_count = faiss_store.live_entry_count(metadata)
        if index.ntotal == 0 or live_count == 0:
            return []

        tombstones = set(metadata["tombstones"])
        query_vec = faiss_store._encode(model, query)

        # Fetch extra candidates to account for tombstones and folder filtering.
        k = min(index.ntotal, limit * 10)
        scores, faiss_ids = index.search(query_vec, k)

        results: List[VectorSearchResult] = []
        for score, fid in zip(scores[0], faiss_ids[0]):
            if fid < 0:
                continue
            if fid in tombstones:
                continue
            entry = metadata["entries"].get(str(fid))
            if entry is None:
                continue
            if folder_name and entry.get("folder") != folder_name:
                continue
            results.append(
                VectorSearchResult(
                    name=entry["name"],
                    folder=entry["folder"],
                    note_id=entry["note_id"],
                    distance=float(score),
                )
            )
            if len(results) >= limit:
                break

        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _index_note_list(notes: List[str], folder_name: str) -> int:
        """Index a list of note names from a given folder. Returns count newly indexed."""
        with _index_lock:
            model = _get_model()
            index, metadata = faiss_store.load()
            indexed = 0

            for i, note_name in enumerate(notes, 1):
                try:
                    note_id = NoteOperations.get_note_id(note_name, folder_name=folder_name)
                    modified_ts = NoteOperations.get_note_modification_timestamp(note_name, folder_name=folder_name)

                    existing_fid = metadata["note_id_to_faiss_id"].get(note_id)
                    if existing_fid is not None:
                        entry = metadata["entries"].get(str(existing_fid), {})
                        needs_reindex = (
                            entry.get("index_version", 0) < faiss_store.INDEX_VERSION
                            or modified_ts > entry.get("modified_ts", 0.0)
                        )
                    else:
                        needs_reindex = True

                    if needs_reindex:
                        _LOGGER.info(f"Indexing ({i}/{len(notes)}): {note_name}")
                        note_details = NoteOperations.get_note_details(note_name, folder_name=folder_name)
                        if VectorSearch._upsert_note(index, metadata, model, note_details):
                            indexed += 1
                    else:
                        _LOGGER.debug(f"Skipping ({i}/{len(notes)}): {note_name} (up-to-date)")
                except Exception as e:
                    _LOGGER.error(f"Failed to process note '{note_name}': {e}")
                    continue

            index, metadata = faiss_store.compact_if_needed(index, metadata, model)
            faiss_store.save(index, metadata)

        _LOGGER.info(f"Indexed {indexed}/{len(notes)} notes in folder '{folder_name}'")
        return indexed

    @staticmethod
    def _upsert_note(
        index,
        metadata: dict,
        model: SentenceTransformer,
        note_details: NoteDetails,
        force: bool = False,
    ) -> bool:
        """
        Encode and upsert a note into the index.

        Tombstones the existing FAISS entry if present, then appends a new one.
        Returns True if the note was (re)indexed, False if skipped.
        """
        note_id = note_details["note_id"]
        name = note_details["name"]
        folder = note_details["folder"]
        body = note_details["body"]
        modified_ts = float(note_details["modified_ts"])

        existing_fid = metadata["note_id_to_faiss_id"].get(note_id)
        if not force and existing_fid is not None:
            entry = metadata["entries"].get(str(existing_fid), {})
            if (
                entry.get("index_version", 0) >= faiss_store.INDEX_VERSION
                and modified_ts <= entry.get("modified_ts", 0.0)
            ):
                return False  # Already up-to-date

        # Tombstone the old slot.
        if existing_fid is not None:
            faiss_store.tombstone(metadata, existing_fid)
            metadata["note_id_to_faiss_id"].pop(note_id, None)

        content = f"{name}\n\n{body}".strip()
        vec = faiss_store._encode(model, content)

        entry = {
            "note_id": note_id,
            "name": name,
            "folder": folder,
            "content": content,
            "modified_ts": modified_ts,
            "indexed_at": _now_ts(),
            "index_version": faiss_store.INDEX_VERSION,
        }
        faiss_store.add_vector(index, metadata, vec, entry)
        return True


def _now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()
