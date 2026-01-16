# applenotes-organization

> An MCP (Model Context Protocol) server for managing Apple Notes on macOS

## Features

- List all notes and notes in specific folders
- Create, read, update, and delete notes
- Search notes by content
- Manage folders (create, delete, list)
- Access account information
- Get note metadata (creation date, modification date, container, etc.)
- Advanced operations like bulk note management

## Installation

### Prerequisites

- macOS with Apple Notes application
- Python 3.10+
- Full Disk Access permission granted to your terminal/IDE

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jmkingsf/applenotes-organization.git
cd applenotes-organization
```

2. Install dependencies:
```bash
pip install -e .
```

3. Grant Full Disk Access (required for AppleScript to access Notes):
   - System Settings → Privacy & Security → Full Disk Access
   - Add your terminal application or IDE

## Usage

### As an MCP Server

Start the MCP server:
```bash
applenotes-mcp
```

The server will start and wait for client connections on stdio.

### Available Tools

The MCP server exposes the following tools:

#### Note Operations
- `list_all_notes` - List all notes
- `list_notes_in_folder` - List notes in a specific folder
- `create_note` - Create a new note
- `read_note` - Read a note's content
- `update_note` - Update a note's body
- `delete_note` - Delete a note
- `move_note` - Move a note to a different folder
- `search_notes` - Search notes by content

#### Note Metadata
- `get_note_creation_date` - Get note creation date
- `get_note_modification_date` - Get note modification date
- `get_note_id` - Get note ID
- `get_note_container` - Get note's folder/container
- `get_note_properties` - Get all note properties

#### Folder Operations
- `list_all_folders` - List all folders
- `create_folder` - Create a new folder
- `delete_folder` - Delete a folder
- `count_notes_in_folder` - Count notes in a folder
- `get_folder_properties` - Get folder properties

#### Account Operations
- `list_all_accounts` - List all accounts
- `get_default_account` - Get the default account
- `list_folders_in_account` - List folders in a specific account

## Reference: Apple commands you can run are:

### Note Operations

**List all notes:**
```bash
osascript -e 'tell application "Notes" to get name of every note'
```

**List notes in a specific folder:**
```bash
osascript -e 'tell application "Notes" to get name of every note of folder "Work"'
```

**Create a new note:**
```bash
osascript -e 'tell application "Notes" to make new note at folder "Notes" with properties {name:"My Note", body:"Note content here"}'
```

**Read a note's content:**
```bash
osascript -e 'tell application "Notes" to get body of note "My Note"'
```

**Move a note to a different folder:**
```bash
osascript -e 'tell application "Notes" to move note "My Note" to folder "Archive"'
```

**Delete a note:**
```bash
osascript -e 'tell application "Notes" to delete note "My Note"'
```

**Search notes by content:**
```bash
osascript -e 'tell application "Notes" to get name of every note whose body contains "keyword"'
```

**Count total notes:**
```bash
osascript -e 'tell application "Notes" to count notes'
```

### Note Metadata

**Get note creation date:**
```bash
osascript -e 'tell application "Notes" to get creation date of note "My Note"'
```

**Get note modification date:**
```bash
osascript -e 'tell application "Notes" to get modification date of note "My Note"'
```

**Get note ID:**
```bash
osascript -e 'tell application "Notes" to get id of note "My Note"'
```

**Get note container (folder):**
```bash
osascript -e 'tell application "Notes" to get container of note "My Note"'
```

**Get all properties of a note:**
```bash
osascript -e 'tell application "Notes" to get properties of note "My Note"'
```

### Folder Operations

**List all folders:**
```bash
osascript -e 'tell application "Notes" to get name of every folder'
```

**Create a new folder:**
```bash
osascript -e 'tell application "Notes" to make new folder with properties {name:"Projects"}'
```

**Delete a folder:**
```bash
osascript -e 'tell application "Notes" to delete folder "Old Folder"'
```

**Count notes in a folder:**
```bash
osascript -e 'tell application "Notes" to count notes of folder "Work"'
```

**Get folder properties:**
```bash
osascript -e 'tell application "Notes" to get properties of folder "Work"'
```

### Account Operations

**List all accounts:**
```bash
osascript -e 'tell application "Notes" to get name of every account'
```

**Get default account:**
```bash
osascript -e 'tell application "Notes" to get default account'
```

**List folders in an account:**
```bash
osascript -e 'tell application "Notes" to get name of every folder of account "iCloud"'
```

### Advanced Operations

**Get the first note in a folder:**
```bash
osascript -e 'tell application "Notes" to get name of first note of folder "Notes"'
```

**Get notes modified in the last day:**
```bash
osascript -e 'tell application "Notes" to get name of every note whose modification date > ((current date) - 1 * days)'
```

**Update note body:**
```bash
osascript -e 'tell application "Notes" to set body of note "My Note" to "Updated content"'
```

**Get HTML content of a note:**
```bash
osascript -e 'tell application "Notes" to get body of note "My Note"'
```

### Complex Operations

For more complex operations, create multi-line AppleScript files (`.scpt` or `.applescript`). Here's an example that exports all notes:

**export_notes.applescript:**
```applescript
tell application "Notes"
    set allNotes to every note
    repeat with aNote in allNotes
        set noteName to name of aNote
        set noteBody to body of aNote
        set noteFolder to name of container of aNote
        -- Process or save the note data here
        log "Note: " & noteName & " in folder: " & noteFolder
    end repeat
end tell
```

Run it with:
```bash
osascript export_notes.applescript
```

### Notes
- The Notes app must be accessible (doesn't need to be open in the UI) for these commands to work
- Note names must be unique within their scope, or you need to reference notes by ID
- HTML formatting in note bodies is preserved
- Some operations may require Full Disk Access permission in System Preferences > Security & Privacy

