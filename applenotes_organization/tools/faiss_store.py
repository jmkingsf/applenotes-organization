"""FAISS persistence layer: index, metadata, and vector storage."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional, Tuple

import faiss
import numpy as np

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

_LOGGER = logging.getLogger(__name__)

# Bump this when the model or indexing logic changes to force a full reindex.
INDEX_VERSION = 2
_MODEL_NAME = "paraphrase-MiniLM-L6-v2"
_DIM = 384

_FAISS_DIR = Path.home() / ".applenotes-organization" / "faiss"
_INDEX_PATH = _FAISS_DIR / "notes.index"
_META_PATH = _FAISS_DIR / "metadata.json"
_VEC_PATH = _FAISS_DIR / "vectors.npy"

# Fraction of tombstoned slots that triggers a compaction.
_COMPACT_THRESHOLD = 0.5


def _empty_metadata() -> dict:
    return {
        "index_version": INDEX_VERSION,
        "model_name": _MODEL_NAME,
        "dim": _DIM,
        "entries": {},            # str(faiss_id) -> entry dict
        "note_id_to_faiss_id": {},  # note_id -> faiss_id (int)
        "tombstones": [],         # list of int faiss_ids that are dead
    }


def load() -> Tuple[faiss.IndexFlatIP, dict]:
    """Load the FAISS index and metadata from disk. Creates fresh ones if missing."""
    _FAISS_DIR.mkdir(parents=True, exist_ok=True)

    if not _META_PATH.exists():
        return _new_index(), _empty_metadata()

    with open(_META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Validate model/version compatibility — purge if mismatched.
    if metadata.get("model_name") != _MODEL_NAME or metadata.get("dim") != _DIM:
        _LOGGER.warning(
            "Model or dimension mismatch in stored index. Purging and starting fresh."
        )
        purge()
        return _new_index(), _empty_metadata()

    if not _INDEX_PATH.exists():
        _LOGGER.warning("FAISS index file missing. Rebuilding from vectors.")
        index = _rebuild_index_from_vectors(metadata)
        faiss.write_index(index, str(_INDEX_PATH))
        return index, metadata

    index = faiss.read_index(str(_INDEX_PATH))
    return index, metadata


def save(index: faiss.IndexFlatIP, metadata: dict) -> None:
    """Persist the FAISS index and metadata to disk."""
    _FAISS_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(_INDEX_PATH))
    with open(_META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def purge() -> None:
    """Delete all FAISS index files."""
    for path in (_INDEX_PATH, _META_PATH, _VEC_PATH):
        if path.exists():
            path.unlink()
    _LOGGER.info("FAISS index purged.")


def add_vector(
    index: faiss.IndexFlatIP,
    metadata: dict,
    vec: np.ndarray,
    entry: dict,
) -> int:
    """
    Append a normalized vector to the index and record its metadata entry.

    Returns the assigned FAISS integer ID.
    """
    faiss_id = int(index.ntotal)
    index.add(vec)

    # Store/grow the parallel numpy array.
    if _VEC_PATH.exists():
        stored = np.load(str(_VEC_PATH))
        combined = np.vstack([stored, vec])
    else:
        combined = vec.copy()
    np.save(str(_VEC_PATH), combined)

    metadata["entries"][str(faiss_id)] = entry
    metadata["note_id_to_faiss_id"][entry["note_id"]] = faiss_id
    return faiss_id


def tombstone(metadata: dict, faiss_id: int) -> None:
    """Mark a FAISS slot as deleted without touching the index."""
    if faiss_id not in metadata["tombstones"]:
        metadata["tombstones"].append(faiss_id)


def compact_if_needed(
    index: faiss.IndexFlatIP,
    metadata: dict,
    model: SentenceTransformer,
) -> Tuple[faiss.IndexFlatIP, dict]:
    """Rebuild the index if tombstone ratio exceeds the threshold."""
    total = index.ntotal
    dead = len(metadata["tombstones"])
    if total == 0 or dead / total < _COMPACT_THRESHOLD:
        return index, metadata
    _LOGGER.info(f"Compacting FAISS index ({dead}/{total} tombstoned slots).")
    return compact(index, metadata, model)


def compact(
    index: faiss.IndexFlatIP,
    metadata: dict,
    model: SentenceTransformer,
) -> Tuple[faiss.IndexFlatIP, dict]:
    """Rebuild the index from scratch, dropping all tombstoned entries."""
    tombstones = set(metadata["tombstones"])
    live_entries = {
        fid: entry
        for fid_str, entry in metadata["entries"].items()
        if (fid := int(fid_str)) not in tombstones
    }

    new_index = _new_index()
    new_meta = _empty_metadata()
    new_vecs: list[np.ndarray] = []

    # Try to reuse stored vectors first; re-encode only if unavailable.
    stored_vecs: Optional[np.ndarray] = None
    if _VEC_PATH.exists():
        stored_vecs = np.load(str(_VEC_PATH))

    for old_fid, entry in live_entries.items():
        if stored_vecs is not None and old_fid < stored_vecs.shape[0]:
            vec = stored_vecs[old_fid : old_fid + 1].astype(np.float32)
        else:
            # Re-encode if the stored vector is missing.
            content = entry.get("content", "")
            vec = _encode(model, content)

        new_fid = int(new_index.ntotal)
        new_index.add(vec)
        new_vecs.append(vec)

        updated_entry = dict(entry)
        new_meta["entries"][str(new_fid)] = updated_entry
        new_meta["note_id_to_faiss_id"][entry["note_id"]] = new_fid

    if new_vecs:
        np.save(str(_VEC_PATH), np.vstack(new_vecs))
    elif _VEC_PATH.exists():
        _VEC_PATH.unlink()

    _LOGGER.info(f"Compaction complete: {len(live_entries)} live entries retained.")
    return new_index, new_meta


def live_entry_count(metadata: dict) -> int:
    """Count non-tombstoned entries."""
    tombstones = set(metadata["tombstones"])
    return sum(1 for fid_str in metadata["entries"] if int(fid_str) not in tombstones)


def _new_index() -> faiss.IndexFlatIP:
    return faiss.IndexFlatIP(_DIM)


def _rebuild_index_from_vectors(metadata: dict) -> faiss.IndexFlatIP:
    """Rebuild a FAISS index from the stored numpy vectors (no re-encoding).

    All slots — including tombstoned ones — must be re-added in order so that
    FAISS integer IDs stay aligned with the metadata entries dict.
    Tombstone filtering happens at search time in Python.
    """
    index = _new_index()
    if not _VEC_PATH.exists():
        return index
    vecs = np.load(str(_VEC_PATH)).astype(np.float32)
    for i in range(vecs.shape[0]):
        index.add(vecs[i : i + 1])
    return index


def _encode(model: SentenceTransformer, text: str) -> np.ndarray:
    """Encode text to a unit-normalized float32 vector of shape (1, dim)."""
    vec = model.encode([text], normalize_embeddings=True, convert_to_numpy=True)
    return vec.astype(np.float32)
