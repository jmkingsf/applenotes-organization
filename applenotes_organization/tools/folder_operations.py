"""Folder operations for Apple Notes MCP server."""

from typing import List, Dict, Any, Optional

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
    def open_folder(folder_name: str) -> Dict[str, str]:
        """
        Open and focus a folder in the Notes app.

        Args:
            folder_name: Name of the folder to open

        Returns:
            Dictionary with status details
        """
        escaped_name = folder_name.replace('"', '\\"')
        script = f'tell application "Notes" to show folder "{escaped_name}"'
        run_inline_applescript(script)
        return {"status": "opened", "folder": folder_name}

    @staticmethod
    def create_subfolder(folder_name: str, parent_folder_name: str) -> Dict[str, str]:
        """
        Create a new folder inside an existing folder.

        Args:
            folder_name: Name of the subfolder to create
            parent_folder_name: Name of the parent folder

        Returns:
            Dictionary with folder creation details
        """
        escaped_name = folder_name.replace('"', '\\"')
        escaped_parent = parent_folder_name.replace('"', '\\"')
        script = (
            f'tell application "Notes" to make new folder at folder "{escaped_parent}" '
            f'with properties {{name:"{escaped_name}"}}'
        )
        run_inline_applescript(script)
        return {"status": "created", "folder": folder_name, "parent": parent_folder_name}

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
    def list_folders_hierarchy() -> str:
        """
        Build a human-readable tree of all folders and their nesting.

        Returns:
            Indented tree string, e.g.:
              iCloud
                Journal
                  Daily Repentance
                Work
        """
        # Fetch "folderName:::containerName" pairs separated by "|||".
        # The nested try blocks are required: the outer catches inaccessible folders
        # (e.g. orphaned Notes internal folders), while the inner catches containers
        # whose parent folder was deleted — those are treated as root-level (cname="").
        script = (
            'tell application "Notes"\n'
            '  set output to ""\n'
            '  repeat with f in (every folder)\n'
            '    try\n'
            '      set fname to name of f\n'
            '      set cObj to container of f\n'
            '      try\n'
            '        set cname to name of cObj\n'
            '      on error\n'
            '        set cname to ""\n'
            '      end try\n'
            '      set output to output & fname & ":::" & cname & "|||"\n'
            '    end try\n'
            '  end repeat\n'
            '  return output\n'
            'end tell'
        )
        raw = run_inline_applescript(script).strip().rstrip("|")
        if not raw:
            return ""

        # Parse into (folder_name, container_name) pairs
        pairs: List[tuple[str, str]] = []
        for chunk in raw.split("|||"):
            chunk = chunk.strip()
            if ":::" not in chunk:
                continue
            name, container = chunk.split(":::", 1)
            pairs.append((name.strip(), container.strip()))

        # Collect account names (containers that are never themselves a folder)
        folder_names = {name for name, _ in pairs}
        accounts = sorted({container for _, container in pairs if container not in folder_names})

        # Build children map: parent -> [child, ...]
        children: Dict[str, List[str]] = {acc: [] for acc in accounts}
        for name, container in pairs:
            children.setdefault(container, [])
            children.setdefault(name, [])
            children[container].append(name)

        # Render tree recursively
        lines: List[str] = []

        def render(node: str, depth: int) -> None:
            prefix = "  " * depth
            label = node if node else "(orphaned)"
            lines.append(f"{prefix}{'📂 ' if depth == 0 else '📁 '}{label}")
            for child in sorted(children.get(node, [])):
                render(child, depth + 1)

        for account in accounts:
            render(account, 0)

        return "\n".join(lines)

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
