"""Error handling utilities for Apple Notes operations."""


class AppleNotesError(Exception):
    """Base exception for Apple Notes operations."""

    pass


class AppleScriptError(AppleNotesError):
    """Exception raised when AppleScript execution fails."""

    pass


class NoteNotFoundError(AppleNotesError):
    """Exception raised when a note is not found."""

    pass


class FolderNotFoundError(AppleNotesError):
    """Exception raised when a folder is not found."""

    pass


def handle_applescript_error(error: str) -> str:
    """
    Process AppleScript error messages and return user-friendly error text.

    Args:
        error: The raw error message from AppleScript

    Returns:
        Cleaned and user-friendly error message
    """
    error_lower = error.lower()

    if "access not determined" in error_lower or "permission denied" in error_lower:
        return (
            "Permission denied. Please grant Full Disk Access to your terminal/IDE "
            "in System Settings > Privacy & Security > Full Disk Access."
        )
    elif "can't find" in error_lower or "doesn't exist" in error_lower:
        return "Note or folder not found. Please verify the name and try again."
    elif "notes" in error_lower and "can't" in error_lower:
        return "Notes application error. Please ensure Apple Notes is properly installed."
    else:
        return f"AppleScript error: {error}"
