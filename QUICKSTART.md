# Quick Start

## Installation (1 minute)

```bash
git clone https://github.com/jmkingsf/applenotes-organization.git
cd applenotes-organization
chmod +x setup.sh
./setup.sh
```

## Enable Full Disk Access (Required!)

1. System Settings → Privacy & Security → Full Disk Access
2. Add your Terminal or IDE
3. Restart your application

## Start the Server

```bash
source venv/bin/activate
applenotes-mcp
```

## Usage Example with Claude

Once the server is running and connected, you can ask Claude to:

- "List all my notes"
- "Create a note called 'Meeting Notes' in the Work folder"
- "Search for notes containing 'project'"
- "Move the 'Project Ideas' note to the Projects folder"
- "Create a new folder called 'Archive'"
- "Show me all notes in the Work folder"
- "Delete the old note called 'TODO'"

## What You Get

✅ 24 MCP tools for complete Apple Notes management
✅ Full CRUD operations on notes
✅ Folder management (create, delete, list)
✅ Search and metadata operations
✅ Account management
✅ Error handling with helpful messages
✅ Type hints and documentation
✅ Unit tests included
✅ macOS optimized with AppleScript backend

## File Structure

```
applenotes_organization/
├── server.py              # Main MCP server
├── tools/
│   ├── note_operations.py
│   ├── folder_operations.py
│   ├── account_operations.py
│   └── applescript_runner.py
└── utils/
    └── error_handler.py

tests/                     # Unit tests
docs/                      # Documentation
```

## Need Help?

- See [INSTALLATION.md](INSTALLATION.md) for detailed setup
- See [EXAMPLES.md](EXAMPLES.md) for tool usage examples
- See [README.md](README.md) for complete documentation

---

**Platform:** macOS only  
**Python:** 3.10+  
**Status:** Ready to test on your Mac ✅
