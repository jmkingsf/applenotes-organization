"""Vector search and indexing operations using LanceDB."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

from .note_operations import NoteOperations, NoteDetails

_LOGGER = logging.getLogger(__name__)


_EMBEDDING_FUNCTION = get_registry().get("sentence-transformers").create(
    name="all-MiniLM-L6-v2"
)

# Index version - increment this when indexing logic changes to trigger reindexing
INDEX_VERSION = 1


class NoteVector(LanceModel):
    """Schema for stored note vectors."""

    note_id: str
    name: str
    folder: str
    content: str = _EMBEDDING_FUNCTION.SourceField()
    vector: Vector(_EMBEDDING_FUNCTION.ndims()) = _EMBEDDING_FUNCTION.VectorField()  # type: ignore[misc]
    created_ts: float
    modified_ts: float
    indexed_at: float
    index_version: int


@dataclass(frozen=True)
class VectorSearchResult:
    """Result for a vector search query."""

    name: str
    folder: str
    note_id: str
    distance: float


class VectorSearch:
    """Vector search operations backed by LanceDB."""

    _DB_DIR = Path.home() / ".applenotes-organization" / "lancedb"
    _TABLE_NAME = "notes"

    @staticmethod
    def index_folder(folder_name: str) -> int:
        """
        Index all notes in a folder.

        Args:
            folder_name: Folder to index

        Returns:
            Number of notes indexed
        """
        _LOGGER.info(f"Starting indexing for folder: {folder_name}")
        notes = NoteOperations.list_notes_in_folder(folder_name)
        if not notes:
            _LOGGER.warning(f"No notes found in folder: {folder_name}")
            return 0

        _LOGGER.info(f"Found {len(notes)} notes to index in folder: {folder_name}")
        table = VectorSearch._get_table()
        index_map = VectorSearch._get_index_map(table, folder_name)
        indexed = 0
        skipped = 0

        for i, note_name in enumerate(notes, 1):
            try:
                note_id = NoteOperations.get_note_id(note_name)
                modified_ts = NoteOperations.get_note_modification_timestamp(note_name)
                indexed_info = index_map.get(note_id)

                # Check if reindexing is needed
                needs_reindex = (
                    indexed_info is None  # Not yet indexed
                    or indexed_info[1] < INDEX_VERSION  # Version mismatch
                    or modified_ts > indexed_info[0]  # Note modified since last index
                )

                if needs_reindex:
                    _LOGGER.info(f"Indexing note ({i}/{len(notes)}): {note_name}")
                    note_details = NoteOperations.get_note_details(note_name, folder_name=folder_name)
                    VectorSearch._upsert_note(table, note_details)
                    indexed += 1
                else:
                    _LOGGER.debug(f"Skipping note ({i}/{len(notes)}): {note_name} (already up-to-date)")
                    skipped += 1
            except Exception as e:
                _LOGGER.error(f"Failed to process note '{note_name}': {e}")
                continue

        _LOGGER.info(f"Indexing complete: {indexed} indexed, {skipped} skipped (folder: {folder_name})")
        return indexed

    @staticmethod
    def reindex_updated_notes(folder_name: Optional[str] = None) -> int:
        """
        Reindex notes that were updated since last index.

        Args:
            folder_name: Optional folder to restrict reindexing

        Returns:
            Number of notes reindexed
        """
        scope = folder_name if folder_name else "all notes"
        _LOGGER.info(f"Starting reindex for {scope}")
        
        table = VectorSearch._get_table()
        index_map = VectorSearch._get_index_map(table, folder_name)

        if folder_name:
            notes = NoteOperations.list_notes_in_folder(folder_name)
        else:
            notes = NoteOperations.list_all_notes()

        _LOGGER.debug(f"Found {len(notes)} total notes, {len(index_map)} previously indexed")
        
        reindexed = 0
        skipped = 0
        for i, note_name in enumerate(notes, 1):
            try:
                note_id = NoteOperations.get_note_id(note_name)
                modified_ts = NoteOperations.get_note_modification_timestamp(note_name)
                indexed_info = index_map.get(note_id)

                # Check if reindexing is needed
                needs_reindex = (
                    indexed_info is None  # Not yet indexed
                    or indexed_info[1] < INDEX_VERSION  # Version mismatch
                    or modified_ts > indexed_info[0]  # Note modified since last index
                )

                if needs_reindex:
                    _LOGGER.debug(f"Reindexing ({i}/{len(notes)}): {note_name} (updated or new)")
                    note_details = NoteOperations.get_note_details(note_name, folder_name=folder_name)
                    VectorSearch._upsert_note(table, note_details)
                    reindexed += 1
                else:
                    skipped += 1
            except Exception as e:
                _LOGGER.error(f"Failed to reindex note '{note_name}': {e}")
                continue

        _LOGGER.info(f"Reindexing complete: {reindexed} notes updated, {skipped} skipped in {scope}")
        return reindexed

    @staticmethod
    def search(query: str, limit: int = 5, folder_name: Optional[str] = None) -> List[VectorSearchResult]:
        """
        Search indexed notes using a vector query.

        Args:
            query: Natural language search query
            limit: Max results to return
            folder_name: Optional folder filter

        Returns:
            List of vector search results
        """
        table = VectorSearch._get_table()
        search = table.search(query)

        if folder_name:
            escaped_folder = VectorSearch._escape_filter_value(folder_name)
            search = search.where(f"folder = '{escaped_folder}'")

        results = search.limit(limit).to_list()
        return [
            VectorSearchResult(
                name=result.get("name", ""),
                folder=result.get("folder", ""),
                note_id=result.get("note_id", ""),
                distance=float(result.get("_distance", 0.0)),
            )
            for result in results
        ]

    @staticmethod
    def _get_table():
        VectorSearch._DB_DIR.mkdir(parents=True, exist_ok=True)
        db = lancedb.connect(str(VectorSearch._DB_DIR))

        # Try to open the table directly - if it exists, check schema compatibility
        try:
            table = db.open_table(VectorSearch._TABLE_NAME)
            
            # Check if the schema has the index_version field
            schema_fields = [field.name for field in table.schema]
            if "index_version" not in schema_fields:
                _LOGGER.warning(f"Table schema outdated, dropping and recreating table: {VectorSearch._TABLE_NAME}")
                db.drop_table(VectorSearch._TABLE_NAME)
                table = db.create_table(VectorSearch._TABLE_NAME, schema=NoteVector)
                _LOGGER.info(f"Created new table with updated schema: {VectorSearch._TABLE_NAME}")
            else:
                _LOGGER.debug(f"Opened existing table: {VectorSearch._TABLE_NAME}")
            
            return table
        except Exception:
            # Table doesn't exist, create it
            _LOGGER.debug(f"Creating new table: {VectorSearch._TABLE_NAME}")
            return db.create_table(VectorSearch._TABLE_NAME, schema=NoteVector)

    @staticmethod
    def _get_index_map(table, folder_name: Optional[str]) -> Dict[str, tuple[float, int]]:
        """Get map of note_id to (indexed_at, index_version) tuples."""
        rows = VectorSearch._table_rows(table)

        if folder_name:
            rows = [row for row in rows if row.get("folder") == folder_name]

        index_map: Dict[str, tuple[float, int]] = {}
        for row in rows:
            note_id = row.get("note_id")
            indexed_at = row.get("indexed_at")
            index_version = row.get("index_version")
            if not note_id:
                continue
            try:
                ts = float(indexed_at or 0.0)
                version = int(index_version or 0)
                index_map[note_id] = (ts, version)
            except (TypeError, ValueError):
                index_map[note_id] = (0.0, 0)

        return index_map

    @staticmethod
    def _upsert_note(table, note_details: NoteDetails) -> None:
        note_id = note_details["note_id"]
        name = note_details["name"]
        folder = note_details["folder"]
        body = note_details["body"]
        created_ts = float(note_details["created_ts"])
        modified_ts = float(note_details["modified_ts"])
        indexed_at = VectorSearch._now_ts()

        content = f"{name}\n\n{body}".strip()
        escaped_note_id = VectorSearch._escape_filter_value(note_id)

        try:
            table.delete(f"note_id = '{escaped_note_id}'")
        except Exception:
            pass

        table.add(
            [
                {
                    "note_id": note_id,
                    "name": name,
                    "folder": folder,
                    "content": content,
                    "created_ts": created_ts,
                    "modified_ts": modified_ts,
                    "indexed_at": indexed_at,
                    "index_version": INDEX_VERSION,
                }
            ]
        )

    @staticmethod
    def _table_rows(table) -> List[Dict[str, str]]:
        if hasattr(table, "to_arrow"):
            return table.to_arrow().to_pylist()
        if hasattr(table, "to_pandas"):
            return table.to_pandas().to_dict(orient="records")
        if hasattr(table, "to_list"):
            return table.to_list()
        return []

    @staticmethod
    def _escape_filter_value(value: str) -> str:
        return value.replace("'", "''")

    @staticmethod
    def _now_ts() -> float:
        return datetime.now(timezone.utc).timestamp()
