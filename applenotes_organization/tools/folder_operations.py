"""Folder operations for Apple Notes MCP server."""

from typing import List, Dict, Any

from .applescript_runner import run_inline_applescript, parse_applescript_list, parse_applescript_dict


class FolderOperations:
    """Handle folder-related operations with Apple Notes."""

    @staticmethod
    def list_all_folders() -> List[str]:
        """
        Get a list of all folders.

        Returns:
            List of folder names
        """
        script = 'tell application "Notes" to get name of every folder'
        output = run_inline_applescript(script)
        return parse_applescript_list(output)

    @staticmethod
    def create_folder(folder_name: str) -> Dict[str, str]:
        """
        Create a new folder.

        Args:
            folder_name: Name of the folder to create

        Returns:
            Dictionary with folder creation details
        """
        escaped_name = folder_name.replace('"', '\\"')
        script = f'tell application "Notes" to make new folder with properties {{name:"{escaped_name}"}}'
        output = run_inline_applescript(script)
        return {"status": "created", "folder": folder_name}

    @staticmethod
    def delete_folder(folder_name: str) -> Dict[str, str]:
        """
        Delete a folder.

        Args:
            folder_name: Name of the folder to delete

        Returns:
            Dictionary with deletion details
        """
        script = f'tell application "Notes" to delete folder "{folder_name}"'
        output = run_inline_applescript(script)
        return {"status": "deleted", "folder": folder_name}

    @staticmethod
    def count_notes_in_folder(folder_name: str) -> int:
        """
        Count the number of notes in a folder.

        Args:
            folder_name: Name of the folder

        Returns:
            Number of notes in the folder
        """
        script = f'tell application "Notes" to count notes of folder "{folder_name}"'
        output = run_inline_applescript(script)
        try:
            return int(output)
        except ValueError:
            return 0

    @staticmethod
    def get_folder_properties(folder_name: str) -> Dict[str, Any]:
        """
        Get properties of a folder.

        Args:
            folder_name: Name of the folder

        Returns:
            Dictionary of folder properties
        """
        script = f'tell application "Notes" to get properties of folder "{folder_name}"'
        output = run_inline_applescript(script)
        return parse_applescript_dict(output)
