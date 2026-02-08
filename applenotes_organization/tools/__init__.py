"""Tools module for Apple Notes operations."""

from .applescript_runner import run_applescript, run_inline_applescript
from .note_operations import NoteOperations
from .folder_operations import FolderOperations
from .vector_search import VectorSearch

__all__ = [
    "run_applescript",
    "run_inline_applescript",
    "NoteOperations",
    "FolderOperations",
    "VectorSearch",
]
