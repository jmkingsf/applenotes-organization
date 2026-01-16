"""Utilities for Apple Notes MCP server."""

from .error_handler import AppleNotesError, handle_applescript_error

__all__ = ["AppleNotesError", "handle_applescript_error"]
