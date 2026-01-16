"""AppleScript runner for executing Apple Notes commands."""

import subprocess
import json
from pathlib import Path
from typing import Any, Dict, Union

from ..utils.error_handler import AppleScriptError, handle_applescript_error


def run_inline_applescript(script: str) -> str:
    """
    Execute an inline AppleScript command.

    Args:
        script: The AppleScript code to execute

    Returns:
        The output from the AppleScript execution

    Raises:
        AppleScriptError: If the AppleScript execution fails
    """
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            friendly_error = handle_applescript_error(error_msg)
            raise AppleScriptError(friendly_error)

        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise AppleScriptError("AppleScript execution timed out after 30 seconds")
    except FileNotFoundError:
        raise AppleScriptError(
            "osascript not found. This tool requires macOS with AppleScript support."
        )


def run_applescript(script_path: Union[str, Path]) -> str:
    """
    Execute an AppleScript file.

    Args:
        script_path: Path to the AppleScript file (.applescript or .scpt)

    Returns:
        The output from the AppleScript execution

    Raises:
        AppleScriptError: If the AppleScript execution fails
    """
    script_file = Path(script_path)

    if not script_file.exists():
        raise AppleScriptError(f"AppleScript file not found: {script_path}")

    try:
        result = subprocess.run(
            ["osascript", str(script_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            friendly_error = handle_applescript_error(error_msg)
            raise AppleScriptError(friendly_error)

        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        raise AppleScriptError("AppleScript execution timed out after 30 seconds")
    except FileNotFoundError:
        raise AppleScriptError(
            "osascript not found. This tool requires macOS with AppleScript support."
        )


def parse_applescript_list(output: str) -> list:
    """
    Parse AppleScript list output into Python list.

    AppleScript lists are typically comma-separated with possible quotes.

    Args:
        output: Raw output from AppleScript

    Returns:
        Parsed list of items
    """
    if not output:
        return []

    # Handle quoted strings
    items = []
    current = ""
    in_quotes = False

    for char in output:
        if char == '"':
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
            items.append(current.strip().strip('"'))
            current = ""
            continue

        current += char

    if current:
        items.append(current.strip().strip('"'))

    return [item for item in items if item]


def parse_applescript_dict(output: str) -> Dict[str, Any]:
    """
    Parse AppleScript record (dict-like) output into Python dict.

    Args:
        output: Raw output from AppleScript

    Returns:
        Parsed dictionary
    """
    # Simple parser for AppleScript record format
    # Format: {key:value, key:value}
    result = {}

    if not output or not output.startswith("{"):
        return result

    # Remove outer braces
    content = output[1:-1] if output.endswith("}") else output[1:]

    # Split by comma, but respect nested structures
    parts = []
    current = ""
    depth = 0

    for char in content:
        if char in "{[":
            depth += 1
        elif char in "}]":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(current.strip())
            current = ""
            continue

        current += char

    if current:
        parts.append(current.strip())

    # Parse key:value pairs
    for part in parts:
        if ":" in part:
            key, value = part.split(":", 1)
            key = key.strip().strip('"')
            value = value.strip().strip('"')
            result[key] = value

    return result
