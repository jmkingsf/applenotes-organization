# Apple Notes MCP Server - Examples

This document provides examples of how to use the applenotes-organization MCP server.

## Starting the Server

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Start the MCP server
applenotes-mcp
```

The server will start and listen for MCP client connections on stdio.

## Using with Claude API

To use this MCP server with the Anthropic Claude API, configure it in your MCP client's configuration file.

### Example Configuration

For cline or other Claude MCP clients, add to your configuration:

```json
{
  "mcpServers": {
    "applenotes": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "applenotes_organization.server"],
      "env": {
        "PYTHONPATH": "/path/to/applenotes-organization"
      }
    }
  }
}
```

## Tool Usage Examples

### List All Notes

```
Tool: list_all_notes
Arguments: (none)

Response:
Found 5 notes:
- Project Ideas
- Meeting Notes
- Shopping List
- Book Review
- Travel Plans
```

### Create a Note

```
Tool: create_note
Arguments:
  - name: "Daily Standup"
  - body: "Team progress updates and blockers"
  - folder: "Work"

Response:
Note 'Daily Standup' created successfully in folder 'Work'
```

### Read a Note

```
Tool: read_note
Arguments:
  - note_name: "Shopping List"

Response:
- Milk
- Bread
- Eggs
- Coffee
- Cheese
```

### Update a Note

```
Tool: update_note
Arguments:
  - note_name: "Shopping List"
  - new_body: "- Milk\n- Bread\n- Eggs\n- Coffee\n- Cheese\n- Butter"

Response:
Note 'Shopping List' updated successfully
```

### Delete a Note

```
Tool: delete_note
Arguments:
  - note_name: "Old Note"

Response:
Note 'Old Note' deleted successfully
```

### Search Notes

```
Tool: search_notes
Arguments:
  - keyword: "meeting"

Response:
Found 3 notes containing 'meeting':
- Team Meeting Notes
- Client Meeting - January
- Meeting Agenda
```

### Create a Folder

```
Tool: create_folder
Arguments:
  - folder_name: "Projects"

Response:
Folder 'Projects' created successfully
```

### Move a Note

```
Tool: move_note
Arguments:
  - note_name: "Project Ideas"
  - target_folder: "Projects"

Response:
Note 'Project Ideas' moved to folder 'Projects'
```

### List Notes in a Folder

```
Tool: list_notes_in_folder
Arguments:
  - folder_name: "Work"

Response:
Found 8 notes in folder 'Work':
- Daily Standup
- Project Update
- Client Feedback
- Team Meeting Notes
- Bug Report
- Feature Request
- Performance Analysis
- Code Review
```

### Count Notes in a Folder

```
Tool: count_notes_in_folder
Arguments:
  - folder_name: "Work"

Response:
Folder 'Work' contains 8 notes
```

### List All Folders

```
Tool: list_all_folders
Arguments: (none)

Response:
Found 6 folders:
- Notes
- Work
- Personal
- Projects
- Archive
- Ideas
```

### Get Note Metadata

```
Tool: get_note_creation_date
Arguments:
  - note_name: "Project Ideas"

Response:
Note 'Project Ideas' created on: Monday, January 15, 2026 at 2:30:45 PM
```

```
Tool: get_note_modification_date
Arguments:
  - note_name: "Project Ideas"

Response:
Note 'Project Ideas' last modified on: Thursday, January 16, 2026 at 10:15:22 AM
```

```
Tool: get_note_container
Arguments:
  - note_name: "Project Ideas"

Response:
Note 'Project Ideas' is in folder: Projects
```

### List All Accounts

```
Tool: list_all_accounts
Arguments: (none)

Response:
Found 2 accounts:
- iCloud
- On My Mac
```

### List Folders in Account

```
Tool: list_folders_in_account
Arguments:
  - account_name: "iCloud"

Response:
Found 6 folders in account 'iCloud':
- Notes
- Work
- Personal
- Projects
- Archive
- Ideas
```

## Troubleshooting

### "Permission denied" Error

If you get permission denied errors, ensure Full Disk Access is granted:

1. Open System Settings
2. Go to Privacy & Security → Full Disk Access
3. Add your terminal application or IDE
4. Restart the application

### "Notes app must be accessible" Error

- Ensure Apple Notes is installed on your Mac
- The Notes app doesn't need to be open, but it must be accessible
- Try running a simple AppleScript command to verify: `osascript -e 'tell application "Notes" to get name of every note'`

### "Note not found" Error

- Verify the note name is spelled correctly
- Check that the note exists in the expected folder
- Note names are case-sensitive

## Advanced Usage

For more complex workflows, you can chain multiple tools together. For example:

1. List all folders to find target folders
2. Create a new folder if needed
3. Create notes in the folder
4. Update notes as needed
5. Search for notes by keyword

This allows you to programmatically organize your Apple Notes.
