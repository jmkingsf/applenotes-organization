"""Note operations for Apple Notes MCP server."""

from typing import List, Dict, Any, Optional, TypedDict


class NoteDetails(TypedDict):
    """Typed structure for vector index note details."""

    note_id: str
    name: str
    folder: str
    body: str
    created_ts: float
    modified_ts: float

from .applescript_runner import (
    run_inline_applescript,
    parse_applescript_list,
    parse_applescript_dict,
)


class NoteOperations:
    """Handle note-related operations with Apple Notes."""

    @staticmethod
    def _escape_string(value: str) -> str:
        return value.replace('"', '\\"')

    @staticmethod
    def list_all_notes() -> List[str]:
        """
        Get a list of all notes.

        Returns:
            List of note names
        """
        script = 'tell application "Notes" to get name of every note'
        output = run_inline_applescript(script)
        return parse_applescript_list(output)

    @staticmethod
    def list_notes_in_folder(folder_name: str) -> List[str]:
        """
        Get a list of notes in a specific folder.

        Args:
            folder_name: Name of the folder

        Returns:
            List of note names in the folder
        """
        escaped_folder = NoteOperations._escape_string(folder_name)
        script = f'tell application "Notes" to get name of every note of folder "{escaped_folder}"'
        output = run_inline_applescript(script)
        return parse_applescript_list(output)

    @staticmethod
    def create_note(
        name: str, body: str, folder_name: str = "Notes"
    ) -> Dict[str, str]:
        """
        Create a new note.

        Args:
            name: Name of the note
            body: Body/content of the note
            folder_name: Name of the folder to create the note in (default: "Notes")

        Returns:
            Dictionary with note creation details
        """
        # Escape quotes in the body
        escaped_body = NoteOperations._escape_string(body)
        escaped_name = NoteOperations._escape_string(name)
        escaped_folder = NoteOperations._escape_string(folder_name)

        script = f'tell application "Notes" to make new note at folder "{escaped_folder}" with properties {{name:"{escaped_name}", body:"{escaped_body}"}}'
        output = run_inline_applescript(script)
        return {"status": "created", "name": name, "folder": folder_name}

    @staticmethod
    def read_note(note_name: str) -> str:
        """
        Read the content of a note.

        Args:
            note_name: Name of the note

        Returns:
            The body/content of the note
        """
        escaped_name = NoteOperations._escape_string(note_name)
        script = f'tell application "Notes" to get body of note "{escaped_name}"'
        output = run_inline_applescript(script)
        return output

    @staticmethod
    def update_note(note_name: str, new_body: str) -> Dict[str, str]:
        """
        Update a note's body content.

        Args:
            note_name: Name of the note
            new_body: New body/content for the note

        Returns:
            Dictionary with update details
        """
        # Escape quotes in the body
        escaped_body = NoteOperations._escape_string(new_body)
        escaped_name = NoteOperations._escape_string(note_name)

        script = f'tell application "Notes" to set body of note "{escaped_name}" to "{escaped_body}"'
        output = run_inline_applescript(script)
        return {"status": "updated", "note": note_name}

    @staticmethod
    def delete_note(note_name: str) -> Dict[str, str]:
        """
        Delete a note.

        Args:
            note_name: Name of the note to delete

        Returns:
            Dictionary with deletion details
        """
        escaped_name = NoteOperations._escape_string(note_name)
        script = f'tell application "Notes" to delete note "{escaped_name}"'
        output = run_inline_applescript(script)
        return {"status": "deleted", "note": note_name}

    @staticmethod
    def move_note(note_name: str, target_folder: str) -> Dict[str, str]:
        """
        Move a note to a different folder.

        Args:
            note_name: Name of the note
            target_folder: Name of the target folder

        Returns:
            Dictionary with move details
        """
        escaped_name = NoteOperations._escape_string(note_name)
        escaped_folder = NoteOperations._escape_string(target_folder)
        script = f'tell application "Notes" to move note "{escaped_name}" to folder "{escaped_folder}"'
        output = run_inline_applescript(script)
        return {"status": "moved", "note": note_name, "folder": target_folder}

    @staticmethod
    def search_notes(keyword: str) -> List[str]:
        """
        Search notes by content.

        Args:
            keyword: Keyword to search for

        Returns:
            List of note names containing the keyword
        """
        escaped_keyword = NoteOperations._escape_string(keyword)
        script = f'tell application "Notes" to get name of every note whose body contains "{escaped_keyword}"'
        output = run_inline_applescript(script)
        return parse_applescript_list(output)

    @staticmethod
    def count_notes() -> int:
        """
        Get the total number of notes.

        Returns:
            Total count of notes
        """
        script = 'tell application "Notes" to count notes'
        output = run_inline_applescript(script)
        try:
            return int(output)
        except ValueError:
            return 0

    @staticmethod
    def get_note_creation_date(note_name: str) -> str:
        """
        Get the creation date of a note.

        Args:
            note_name: Name of the note

        Returns:
            Creation date of the note
        """
        escaped_name = NoteOperations._escape_string(note_name)
        script = f'tell application "Notes" to get creation date of note "{escaped_name}"'
        output = run_inline_applescript(script)
        return output

    @staticmethod
    def get_note_modification_date(note_name: str) -> str:
        """
        Get the modification date of a note.

        Args:
            note_name: Name of the note

        Returns:
            Modification date of the note
        """
        escaped_name = NoteOperations._escape_string(note_name)
        script = f'tell application "Notes" to get modification date of note "{escaped_name}"'
        output = run_inline_applescript(script)
        return output

    @staticmethod
    def get_note_id(note_name: str) -> str:
        """
        Get the ID of a note.

        Args:
            note_name: Name of the note

        Returns:
            ID of the note
        """
        escaped_name = NoteOperations._escape_string(note_name)
        script = f'tell application "Notes" to get id of note "{escaped_name}"'
        output = run_inline_applescript(script)
        return output

    @staticmethod
    def get_note_container(note_name: str, folder_name: Optional[str] = None) -> str:
        """
        Get the container (folder) of a note.

        Args:
            note_name: Name of the note
            folder_name: Optional folder name to disambiguate if multiple notes have the same name

        Returns:
            Folder/container name of the note
        """
        escaped_name = NoteOperations._escape_string(note_name)
        
        # If folder is provided, query within that folder context for better accuracy
        if folder_name:
            escaped_folder = NoteOperations._escape_string(folder_name)
            script = f'tell application "Notes" to get name of container of note "{escaped_name}" of folder "{escaped_folder}"'
        else:
            script = f'tell application "Notes" to get name of container of note "{escaped_name}"'
        
        output = run_inline_applescript(script)
        return output

    @staticmethod
    def get_note_properties(note_name: str) -> Dict[str, Any]:
        """
        Get all properties of a note.

        Args:
            note_name: Name of the note

        Returns:
            Dictionary of note properties
        """
        escaped_name = NoteOperations._escape_string(note_name)
        script = f'tell application "Notes" to get properties of note "{escaped_name}"'
        output = run_inline_applescript(script)
        return parse_applescript_dict(output)

    @staticmethod
    def get_note_creation_timestamp(note_name: str) -> float:
        """
        Get the creation date of a note as a Unix timestamp.

        Args:
            note_name: Name of the note

        Returns:
            Creation date as Unix timestamp
        """
        escaped_name = NoteOperations._escape_string(note_name)
        script = (
            'tell application "Notes" to get (creation date of note '
            f'"{escaped_name}") - (date "January 1, 1970")'
        )
        output = run_inline_applescript(script)
        try:
            return float(output)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def get_note_modification_timestamp(note_name: str) -> float:
        """
        Get the modification date of a note as a Unix timestamp.

        Args:
            note_name: Name of the note

        Returns:
            Modification date as Unix timestamp
        """
        escaped_name = NoteOperations._escape_string(note_name)
        script = (
            'tell application "Notes" to get (modification date of note '
            f'"{escaped_name}") - (date "January 1, 1970")'
        )
        output = run_inline_applescript(script)
        try:
            return float(output)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def get_note_details(note_name: str, folder_name: Optional[str] = None) -> NoteDetails:
        """
        Get the details required for vector indexing.

        Args:
            note_name: Name of the note
            folder_name: Optional folder name to disambiguate note lookup

        Returns:
            Dictionary of note details
        """
        # Use provided folder_name instead of querying for it if available
        container = folder_name if folder_name else NoteOperations.get_note_container(note_name)
        
        return {
            "note_id": NoteOperations.get_note_id(note_name),
            "name": note_name,
            "folder": container,
            "body": NoteOperations.read_note(note_name),
            "created_ts": NoteOperations.get_note_creation_timestamp(note_name),
            "modified_ts": NoteOperations.get_note_modification_timestamp(note_name),
        }
