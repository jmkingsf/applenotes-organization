"""Main MCP server for Apple Notes organization tool."""

import sys
import json
from typing import Any, Dict, List

from fastmcp import Server
from fastmcp.types import Tool, TextContent

from .tools.note_operations import NoteOperations
from .tools.folder_operations import FolderOperations
from .tools.account_operations import AccountOperations
from .utils.error_handler import AppleNotesError


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("applenotes-organization")

    # Note operations tools
    @server.call_tool()
    def list_all_notes(arguments: Dict[str, Any]) -> List[TextContent]:
        """List all notes in Apple Notes."""
        try:
            notes = NoteOperations.list_all_notes()
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(notes)} notes:\n" + "\n".join(f"- {note}" for note in notes),
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "list_all_notes",
        Tool(
            name="list_all_notes",
            description="List all notes in Apple Notes",
            inputSchema={"type": "object", "properties": {}},
        ),
    )

    @server.call_tool()
    def list_notes_in_folder(arguments: Dict[str, Any]) -> List[TextContent]:
        """List notes in a specific folder."""
        try:
            folder_name = arguments.get("folder_name")
            if not folder_name:
                return [TextContent(type="text", text="Error: folder_name is required")]

            notes = NoteOperations.list_notes_in_folder(folder_name)
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(notes)} notes in folder '{folder_name}':\n"
                    + "\n".join(f"- {note}" for note in notes),
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "list_notes_in_folder",
        Tool(
            name="list_notes_in_folder",
            description="List notes in a specific folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {"type": "string", "description": "Name of the folder"}
                },
                "required": ["folder_name"],
            },
        ),
    )

    @server.call_tool()
    def create_note(arguments: Dict[str, Any]) -> List[TextContent]:
        """Create a new note."""
        try:
            name = arguments.get("name")
            body = arguments.get("body", "")
            folder = arguments.get("folder", "Notes")

            if not name:
                return [TextContent(type="text", text="Error: name is required")]

            result = NoteOperations.create_note(name, body, folder)
            return [
                TextContent(
                    type="text",
                    text=f"Note '{name}' created successfully in folder '{folder}'",
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "create_note",
        Tool(
            name="create_note",
            description="Create a new note",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the note"},
                    "body": {"type": "string", "description": "Body/content of the note"},
                    "folder": {
                        "type": "string",
                        "description": "Folder to create the note in (default: Notes)",
                    },
                },
                "required": ["name"],
            },
        ),
    )

    @server.call_tool()
    def read_note(arguments: Dict[str, Any]) -> List[TextContent]:
        """Read the content of a note."""
        try:
            note_name = arguments.get("note_name")
            if not note_name:
                return [TextContent(type="text", text="Error: note_name is required")]

            content = NoteOperations.read_note(note_name)
            return [TextContent(type="text", text=content)]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "read_note",
        Tool(
            name="read_note",
            description="Read the content of a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_name": {"type": "string", "description": "Name of the note"}
                },
                "required": ["note_name"],
            },
        ),
    )

    @server.call_tool()
    def update_note(arguments: Dict[str, Any]) -> List[TextContent]:
        """Update a note's body content."""
        try:
            note_name = arguments.get("note_name")
            new_body = arguments.get("new_body")

            if not note_name or new_body is None:
                return [TextContent(type="text", text="Error: note_name and new_body are required")]

            result = NoteOperations.update_note(note_name, new_body)
            return [TextContent(type="text", text=f"Note '{note_name}' updated successfully")]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "update_note",
        Tool(
            name="update_note",
            description="Update a note's body content",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_name": {"type": "string", "description": "Name of the note"},
                    "new_body": {"type": "string", "description": "New body content"},
                },
                "required": ["note_name", "new_body"],
            },
        ),
    )

    @server.call_tool()
    def delete_note(arguments: Dict[str, Any]) -> List[TextContent]:
        """Delete a note."""
        try:
            note_name = arguments.get("note_name")
            if not note_name:
                return [TextContent(type="text", text="Error: note_name is required")]

            result = NoteOperations.delete_note(note_name)
            return [TextContent(type="text", text=f"Note '{note_name}' deleted successfully")]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "delete_note",
        Tool(
            name="delete_note",
            description="Delete a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_name": {"type": "string", "description": "Name of the note"}
                },
                "required": ["note_name"],
            },
        ),
    )

    @server.call_tool()
    def move_note(arguments: Dict[str, Any]) -> List[TextContent]:
        """Move a note to a different folder."""
        try:
            note_name = arguments.get("note_name")
            target_folder = arguments.get("target_folder")

            if not note_name or not target_folder:
                return [
                    TextContent(
                        type="text", text="Error: note_name and target_folder are required"
                    )
                ]

            result = NoteOperations.move_note(note_name, target_folder)
            return [
                TextContent(
                    type="text",
                    text=f"Note '{note_name}' moved to folder '{target_folder}'",
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "move_note",
        Tool(
            name="move_note",
            description="Move a note to a different folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_name": {"type": "string", "description": "Name of the note"},
                    "target_folder": {"type": "string", "description": "Target folder name"},
                },
                "required": ["note_name", "target_folder"],
            },
        ),
    )

    @server.call_tool()
    def search_notes(arguments: Dict[str, Any]) -> List[TextContent]:
        """Search notes by content."""
        try:
            keyword = arguments.get("keyword")
            if not keyword:
                return [TextContent(type="text", text="Error: keyword is required")]

            notes = NoteOperations.search_notes(keyword)
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(notes)} notes containing '{keyword}':\n"
                    + "\n".join(f"- {note}" for note in notes),
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "search_notes",
        Tool(
            name="search_notes",
            description="Search notes by content keyword",
            inputSchema={
                "type": "object",
                "properties": {"keyword": {"type": "string", "description": "Keyword to search for"}},
                "required": ["keyword"],
            },
        ),
    )

    @server.call_tool()
    def count_notes(arguments: Dict[str, Any]) -> List[TextContent]:
        """Get the total number of notes."""
        try:
            count = NoteOperations.count_notes()
            return [TextContent(type="text", text=f"Total notes: {count}")]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "count_notes",
        Tool(
            name="count_notes",
            description="Get the total number of notes",
            inputSchema={"type": "object", "properties": {}},
        ),
    )

    @server.call_tool()
    def get_note_creation_date(arguments: Dict[str, Any]) -> List[TextContent]:
        """Get the creation date of a note."""
        try:
            note_name = arguments.get("note_name")
            if not note_name:
                return [TextContent(type="text", text="Error: note_name is required")]

            creation_date = NoteOperations.get_note_creation_date(note_name)
            return [
                TextContent(
                    type="text",
                    text=f"Note '{note_name}' created on: {creation_date}",
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "get_note_creation_date",
        Tool(
            name="get_note_creation_date",
            description="Get the creation date of a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_name": {"type": "string", "description": "Name of the note"}
                },
                "required": ["note_name"],
            },
        ),
    )

    @server.call_tool()
    def get_note_modification_date(arguments: Dict[str, Any]) -> List[TextContent]:
        """Get the modification date of a note."""
        try:
            note_name = arguments.get("note_name")
            if not note_name:
                return [TextContent(type="text", text="Error: note_name is required")]

            mod_date = NoteOperations.get_note_modification_date(note_name)
            return [
                TextContent(
                    type="text",
                    text=f"Note '{note_name}' last modified on: {mod_date}",
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "get_note_modification_date",
        Tool(
            name="get_note_modification_date",
            description="Get the modification date of a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_name": {"type": "string", "description": "Name of the note"}
                },
                "required": ["note_name"],
            },
        ),
    )

    @server.call_tool()
    def get_note_id(arguments: Dict[str, Any]) -> List[TextContent]:
        """Get the ID of a note."""
        try:
            note_name = arguments.get("note_name")
            if not note_name:
                return [TextContent(type="text", text="Error: note_name is required")]

            note_id = NoteOperations.get_note_id(note_name)
            return [TextContent(type="text", text=f"Note '{note_name}' ID: {note_id}")]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "get_note_id",
        Tool(
            name="get_note_id",
            description="Get the ID of a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_name": {"type": "string", "description": "Name of the note"}
                },
                "required": ["note_name"],
            },
        ),
    )

    @server.call_tool()
    def get_note_container(arguments: Dict[str, Any]) -> List[TextContent]:
        """Get the container (folder) of a note."""
        try:
            note_name = arguments.get("note_name")
            if not note_name:
                return [TextContent(type="text", text="Error: note_name is required")]

            container = NoteOperations.get_note_container(note_name)
            return [
                TextContent(type="text", text=f"Note '{note_name}' is in folder: {container}")
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "get_note_container",
        Tool(
            name="get_note_container",
            description="Get the container (folder) of a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_name": {"type": "string", "description": "Name of the note"}
                },
                "required": ["note_name"],
            },
        ),
    )

    @server.call_tool()
    def get_note_properties(arguments: Dict[str, Any]) -> List[TextContent]:
        """Get all properties of a note."""
        try:
            note_name = arguments.get("note_name")
            if not note_name:
                return [TextContent(type="text", text="Error: note_name is required")]

            properties = NoteOperations.get_note_properties(note_name)
            props_text = "\n".join(f"{k}: {v}" for k, v in properties.items())
            return [
                TextContent(
                    type="text",
                    text=f"Properties for note '{note_name}':\n{props_text}",
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "get_note_properties",
        Tool(
            name="get_note_properties",
            description="Get all properties of a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_name": {"type": "string", "description": "Name of the note"}
                },
                "required": ["note_name"],
            },
        ),
    )

    # Folder operations tools
    @server.call_tool()
    def list_all_folders(arguments: Dict[str, Any]) -> List[TextContent]:
        """List all folders."""
        try:
            folders = FolderOperations.list_all_folders()
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(folders)} folders:\n"
                    + "\n".join(f"- {folder}" for folder in folders),
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "list_all_folders",
        Tool(
            name="list_all_folders",
            description="List all folders in Apple Notes",
            inputSchema={"type": "object", "properties": {}},
        ),
    )

    @server.call_tool()
    def create_folder(arguments: Dict[str, Any]) -> List[TextContent]:
        """Create a new folder."""
        try:
            folder_name = arguments.get("folder_name")
            if not folder_name:
                return [TextContent(type="text", text="Error: folder_name is required")]

            result = FolderOperations.create_folder(folder_name)
            return [TextContent(type="text", text=f"Folder '{folder_name}' created successfully")]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "create_folder",
        Tool(
            name="create_folder",
            description="Create a new folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {"type": "string", "description": "Name of the folder"}
                },
                "required": ["folder_name"],
            },
        ),
    )

    @server.call_tool()
    def delete_folder(arguments: Dict[str, Any]) -> List[TextContent]:
        """Delete a folder."""
        try:
            folder_name = arguments.get("folder_name")
            if not folder_name:
                return [TextContent(type="text", text="Error: folder_name is required")]

            result = FolderOperations.delete_folder(folder_name)
            return [TextContent(type="text", text=f"Folder '{folder_name}' deleted successfully")]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "delete_folder",
        Tool(
            name="delete_folder",
            description="Delete a folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {"type": "string", "description": "Name of the folder"}
                },
                "required": ["folder_name"],
            },
        ),
    )

    @server.call_tool()
    def count_notes_in_folder(arguments: Dict[str, Any]) -> List[TextContent]:
        """Count the number of notes in a folder."""
        try:
            folder_name = arguments.get("folder_name")
            if not folder_name:
                return [TextContent(type="text", text="Error: folder_name is required")]

            count = FolderOperations.count_notes_in_folder(folder_name)
            return [
                TextContent(type="text", text=f"Folder '{folder_name}' contains {count} notes")
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "count_notes_in_folder",
        Tool(
            name="count_notes_in_folder",
            description="Count notes in a folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {"type": "string", "description": "Name of the folder"}
                },
                "required": ["folder_name"],
            },
        ),
    )

    @server.call_tool()
    def get_folder_properties(arguments: Dict[str, Any]) -> List[TextContent]:
        """Get properties of a folder."""
        try:
            folder_name = arguments.get("folder_name")
            if not folder_name:
                return [TextContent(type="text", text="Error: folder_name is required")]

            properties = FolderOperations.get_folder_properties(folder_name)
            props_text = "\n".join(f"{k}: {v}" for k, v in properties.items())
            return [
                TextContent(
                    type="text",
                    text=f"Properties for folder '{folder_name}':\n{props_text}",
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "get_folder_properties",
        Tool(
            name="get_folder_properties",
            description="Get properties of a folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_name": {"type": "string", "description": "Name of the folder"}
                },
                "required": ["folder_name"],
            },
        ),
    )

    # Account operations tools
    @server.call_tool()
    def list_all_accounts(arguments: Dict[str, Any]) -> List[TextContent]:
        """List all accounts."""
        try:
            accounts = AccountOperations.list_all_accounts()
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(accounts)} accounts:\n"
                    + "\n".join(f"- {account}" for account in accounts),
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "list_all_accounts",
        Tool(
            name="list_all_accounts",
            description="List all accounts in Apple Notes",
            inputSchema={"type": "object", "properties": {}},
        ),
    )

    @server.call_tool()
    def get_default_account(arguments: Dict[str, Any]) -> List[TextContent]:
        """Get the default account."""
        try:
            account = AccountOperations.get_default_account()
            return [TextContent(type="text", text=f"Default account: {account}")]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "get_default_account",
        Tool(
            name="get_default_account",
            description="Get the default account",
            inputSchema={"type": "object", "properties": {}},
        ),
    )

    @server.call_tool()
    def list_folders_in_account(arguments: Dict[str, Any]) -> List[TextContent]:
        """List folders in an account."""
        try:
            account_name = arguments.get("account_name")
            if not account_name:
                return [TextContent(type="text", text="Error: account_name is required")]

            folders = AccountOperations.list_folders_in_account(account_name)
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(folders)} folders in account '{account_name}':\n"
                    + "\n".join(f"- {folder}" for folder in folders),
                )
            ]
        except AppleNotesError as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    server.set_tool_for_function(
        "list_folders_in_account",
        Tool(
            name="list_folders_in_account",
            description="List folders in an account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_name": {"type": "string", "description": "Name of the account"}
                },
                "required": ["account_name"],
            },
        ),
    )

    return server


def main():
    """Run the MCP server."""
    server = create_server()
    server.run(sys.stdin.buffer, sys.stdout.buffer)


if __name__ == "__main__":
    main()
