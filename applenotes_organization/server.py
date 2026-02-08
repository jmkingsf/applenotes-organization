"""Main MCP server for Apple Notes organization tool."""

import logging

from fastmcp import FastMCP

from . import __description__, __version__
from .tools.note_operations import NoteOperations
from .tools.folder_operations import FolderOperations
from .tools.vector_search import VectorSearch
from .utils.error_handler import AppleNotesError


# Configure logging to output to console (MCP output window)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# Create FastMCP server
mcp = FastMCP(
    name="applenotes-organization",
    instructions=__description__,
    version=__version__,
    website_url="https://github.com/jmkingsf/applenotes-organization",
)


# ============================================================================
# NOTE OPERATIONS
# ============================================================================

@mcp.tool()
def list_all_notes() -> str:
    """List all notes in Apple Notes."""
    try:
        notes = NoteOperations.list_all_notes()
        return f"Found {len(notes)} notes:\n" + "\n".join(f"- {note}" for note in notes)
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def list_notes_in_folder(folder_name: str) -> str:
    """List notes in a specific folder.
    
    Args:
        folder_name: Name of the folder to list notes from
    """
    try:
        notes = NoteOperations.list_notes_in_folder(folder_name)
        return f"Found {len(notes)} notes in folder '{folder_name}':\n" + "\n".join(f"- {note}" for note in notes)
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def create_note(name: str, body: str = "", folder: str = "Notes") -> str:
    """Create a new note.
    
    Args:
        name: Name of the note to create
        body: Body/content of the note (default: empty)
        folder: Folder to create the note in (default: "Notes")
    """
    try:
        NoteOperations.create_note(name, body, folder)
        return f"Note '{name}' created successfully in folder '{folder}'"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def read_note(note_name: str) -> str:
    """Read the content of a note.
    
    Args:
        note_name: Name of the note to read
    """
    try:
        content = NoteOperations.read_note(note_name)
        return content
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def update_note(note_name: str, new_body: str) -> str:
    """Update a note's body content.
    
    Args:
        note_name: Name of the note to update
        new_body: New body content for the note
    """
    try:
        NoteOperations.update_note(note_name, new_body)
        return f"Note '{note_name}' updated successfully"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def delete_note(note_name: str) -> str:
    """Delete a note.
    
    Args:
        note_name: Name of the note to delete
    """
    try:
        NoteOperations.delete_note(note_name)
        return f"Note '{note_name}' deleted successfully"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def move_note(note_name: str, target_folder: str) -> str:
    """Move a note to a different folder.
    
    Args:
        note_name: Name of the note to move
        target_folder: Target folder name
    """
    try:
        NoteOperations.move_note(note_name, target_folder)
        return f"Note '{note_name}' moved to folder '{target_folder}'"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def search_notes(keyword: str) -> str:
    """Search notes by content keyword.
    
    Args:
        keyword: Keyword to search for in note content
    """
    try:
        notes = NoteOperations.search_notes(keyword)
        return f"Found {len(notes)} notes containing '{keyword}':\n" + "\n".join(f"- {note}" for note in notes)
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def count_notes() -> str:
    """Get the total number of notes."""
    try:
        count = NoteOperations.count_notes()
        return f"Total notes: {count}"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_note_creation_date(note_name: str) -> str:
    """Get the creation date of a note.
    
    Args:
        note_name: Name of the note
    """
    try:
        creation_date = NoteOperations.get_note_creation_date(note_name)
        return f"Note '{note_name}' created on: {creation_date}"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_note_modification_date(note_name: str) -> str:
    """Get the modification date of a note.
    
    Args:
        note_name: Name of the note
    """
    try:
        mod_date = NoteOperations.get_note_modification_date(note_name)
        return f"Note '{note_name}' last modified on: {mod_date}"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_note_id(note_name: str) -> str:
    """Get the ID of a note.
    
    Args:
        note_name: Name of the note
    """
    try:
        note_id = NoteOperations.get_note_id(note_name)
        return f"Note '{note_name}' ID: {note_id}"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_note_container(note_name: str) -> str:
    """Get the container (folder) of a note.
    
    Args:
        note_name: Name of the note
    """
    try:
        container = NoteOperations.get_note_container(note_name)
        return f"Note '{note_name}' is in folder: {container}"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_note_properties(note_name: str) -> str:
    """Get all properties of a note.
    
    Args:
        note_name: Name of the note
    """
    try:
        properties = NoteOperations.get_note_properties(note_name)
        props_text = "\n".join(f"{k}: {v}" for k, v in properties.items())
        return f"Properties for note '{note_name}':\n{props_text}"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


# ============================================================================
# FOLDER OPERATIONS
# ============================================================================

@mcp.tool()
def list_all_folders() -> str:
    """List all folders in Apple Notes."""
    try:
        folders = FolderOperations.list_all_folders()
        return f"Found {len(folders)} folders:\n" + "\n".join(f"- {folder}" for folder in folders)
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def create_folder(folder_name: str) -> str:
    """Create a new folder.
    
    Args:
        folder_name: Name of the folder to create
    """
    try:
        FolderOperations.create_folder(folder_name)
        return f"Folder '{folder_name}' created successfully"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def delete_folder(folder_name: str) -> str:
    """Delete a folder.
    
    Args:
        folder_name: Name of the folder to delete
    """
    try:
        FolderOperations.delete_folder(folder_name)
        return f"Folder '{folder_name}' deleted successfully"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def count_notes_in_folder(folder_name: str) -> str:
    """Count notes in a folder.
    
    Args:
        folder_name: Name of the folder
    """
    try:
        count = FolderOperations.count_notes_in_folder(folder_name)
        return f"Folder '{folder_name}' contains {count} notes"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_folder_properties(folder_name: str) -> str:
    """Get properties of a folder.
    
    Args:
        folder_name: Name of the folder
    """
    try:
        properties = FolderOperations.get_folder_properties(folder_name)
        props_text = "\n".join(f"{k}: {v}" for k, v in properties.items())
        return f"Properties for folder '{folder_name}':\n{props_text}"
    except AppleNotesError as e:
        return f"Error: {str(e)}"


# ============================================================================
# VECTOR SEARCH OPERATIONS
# ============================================================================

@mcp.tool()
def index_notes_in_folder(folder_name: str) -> str:
    """Index all notes in a folder for vector search.

    Args:
        folder_name: Name of the folder to index
    """
    try:
        indexed = VectorSearch.index_folder(folder_name)
        return f"Indexed {indexed} notes in folder '{folder_name}'."
    except (AppleNotesError, Exception) as e:
        return f"Error: {str(e)}"


@mcp.tool()
def reindex_notes_since_last_index(folder_name: str = "") -> str:
    """Reindex notes updated since the last index.

    Args:
        folder_name: Optional folder name to scope reindexing
    """
    try:
        scoped_folder = folder_name or None
        reindexed = VectorSearch.reindex_updated_notes(scoped_folder)
        scope_text = f" in folder '{folder_name}'" if folder_name else ""
        return f"Reindexed {reindexed} notes{scope_text}."
    except (AppleNotesError, Exception) as e:
        return f"Error: {str(e)}"


@mcp.tool()
def search_notes_vector(query: str, limit: int = 5, folder_name: str = "") -> str:
    """Search notes using vector similarity.

    Args:
        query: Natural language search query
        limit: Maximum number of results
        folder_name: Optional folder name to scope search
    """
    try:
        scoped_folder = folder_name or None
        results = VectorSearch.search(query, limit=limit, folder_name=scoped_folder)

        if not results:
            return "No vector search results found."

        lines = [
            f"- {result.name} (folder: {result.folder}, score: {result.distance:.4f})"
            for result in results
        ]
        return f"Found {len(results)} results:\n" + "\n".join(lines)
    except (AppleNotesError, Exception) as e:
        return f"Error: {str(e)}"

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
