"""Note operations for Apple Notes MCP server."""

from typing import List, Dict, Any, Optional

from .applescript_runner import (
    run_inline_applescript,
    parse_applescript_list,
    parse_applescript_dict,
)


class NoteOperations:
    """Handle note-related operations with Apple Notes."""

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
        script = f'tell application "Notes" to get name of every note of folder "{folder_name}"'
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
        escaped_body = body.replace('"', '\\"')
        escaped_name = name.replace('"', '\\"')

        script = f'tell application "Notes" to make new note at folder "{folder_name}" with properties {{name:"{escaped_name}", body:"{escaped_body}"}}'
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
        script = f'tell application "Notes" to get body of note "{note_name}"'
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
        escaped_body = new_body.replace('"', '\\"')

        script = f'tell application "Notes" to set body of note "{note_name}" to "{escaped_body}"'
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
        script = f'tell application "Notes" to delete note "{note_name}"'
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
        script = f'tell application "Notes" to move note "{note_name}" to folder "{target_folder}"'
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
        script = f'tell application "Notes" to get name of every note whose body contains "{keyword}"'
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
        script = f'tell application "Notes" to get creation date of note "{note_name}"'
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
        script = f'tell application "Notes" to get modification date of note "{note_name}"'
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
        script = f'tell application "Notes" to get id of note "{note_name}"'
        output = run_inline_applescript(script)
        return output

    @staticmethod
    def get_note_container(note_name: str) -> str:
        """
        Get the container (folder) of a note.

        Args:
            note_name: Name of the note

        Returns:
            Folder/container name of the note
        """
        script = f'tell application "Notes" to get name of container of note "{note_name}"'
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
        script = f'tell application "Notes" to get properties of note "{note_name}"'
        output = run_inline_applescript(script)
        return parse_applescript_dict(output)
