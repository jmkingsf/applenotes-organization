# Installation & Setup Guide

## Prerequisites

- macOS with Apple Notes application installed
- Python 3.10 or later
- Terminal or IDE with Full Disk Access permission

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/jmkingsf/applenotes-organization.git
cd applenotes-organization
```

### 2. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Check Python version (3.10+)
- Create a virtual environment
- Install the package and dependencies

### 3. Grant Full Disk Access (IMPORTANT)

The MCP server requires Full Disk Access to interact with Apple Notes:

1. Open **System Settings**
2. Go to **Privacy & Security → Full Disk Access**
3. Add your terminal application or IDE to the list
4. You may need to restart your application

### 4. Start the Server

Activate the virtual environment and start the MCP server:

```bash
source venv/bin/activate
applenotes-mcp
```

The server will start and wait for connections on stdio.

## Configuration for MCP Clients

### Using with Anthropic Claude

Add this to your MCP client configuration:

```json
{
  "mcpServers": {
    "applenotes": {
      "command": "applenotes-mcp"
    }
  }
}
```

## Available Tools

The MCP server exposes 24 tools for managing Apple Notes:

### Note Operations (8 tools)
- `list_all_notes` - List all notes
- `list_notes_in_folder` - List notes in a folder
- `create_note` - Create a new note
- `read_note` - Read a note's content
- `update_note` - Update a note's body
- `delete_note` - Delete a note
- `move_note` - Move a note to a folder
- `search_notes` - Search notes by content

### Note Metadata (5 tools)
- `count_notes` - Count total notes
- `get_note_creation_date` - Get creation date
- `get_note_modification_date` - Get modification date
- `get_note_id` - Get note ID
- `get_note_container` - Get note's folder
- `get_note_properties` - Get all properties

### Folder Operations (5 tools)
- `list_all_folders` - List all folders
- `create_folder` - Create a new folder
- `delete_folder` - Delete a folder
- `count_notes_in_folder` - Count notes in folder
- `get_folder_properties` - Get folder properties

### Account Operations (3 tools)
- `list_all_accounts` - List all accounts
- `get_default_account` - Get default account
- `list_folders_in_account` - List folders in account

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black applenotes_organization/
ruff check applenotes_organization/
```

## Project Structure

```
applenotes-organization/
├── applenotes_organization/          # Main package
│   ├── __init__.py
│   ├── server.py                     # MCP server implementation
│   ├── tools/
│   │   ├── applescript_runner.py     # AppleScript execution
│   │   ├── note_operations.py        # Note CRUD operations
│   │   ├── folder_operations.py      # Folder management
│   │   └── account_operations.py     # Account management
│   └── utils/
│       └── error_handler.py          # Error handling
├── tests/                             # Unit tests
├── pyproject.toml                     # Python project config
├── setup.sh                           # Installation script
├── LICENSE                            # MIT License
├── README.md                          # Project README
├── EXAMPLES.md                        # Usage examples
└── .github/
    └── workflows/
        └── tests.yml                  # CI/CD configuration
```

## Troubleshooting

### "Permission denied" Error

Ensure Full Disk Access is granted to your terminal/IDE:
1. System Settings → Privacy & Security → Full Disk Access
2. Add your terminal or IDE
3. Restart the application

### "osascript not found"

This tool requires macOS with AppleScript support. Ensure you're running on macOS.

### "Notes app must be accessible"

- Verify Apple Notes is installed
- The app doesn't need to be open, but must be accessible
- Try: `osascript -e 'tell application "Notes" to get name of every note'`

## Support

For issues or questions, please open a [GitHub Issue](https://github.com/jmkingsf/applenotes-organization/issues).

## License

MIT License - See [LICENSE](LICENSE) file for details.
