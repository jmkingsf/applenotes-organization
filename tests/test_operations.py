"""Tests for Apple Notes operations."""

import pytest
from applenotes_organization.tools.applescript_runner import (
    parse_applescript_list,
    parse_applescript_dict,
)


class TestAppleScriptParsing:
    """Test AppleScript output parsing."""

    def test_parse_empty_list(self):
        """Test parsing empty list."""
        assert parse_applescript_list("") == []

    def test_parse_single_item_list(self):
        """Test parsing single item list."""
        result = parse_applescript_list("Note1")
        assert "Note1" in result

    def test_parse_multiple_items_list(self):
        """Test parsing multiple items list."""
        result = parse_applescript_list('"Note1", "Note2", "Note3"')
        assert len(result) == 3
        assert "Note1" in result
        assert "Note2" in result
        assert "Note3" in result

    def test_parse_empty_dict(self):
        """Test parsing empty dict."""
        result = parse_applescript_dict("{}")
        assert result == {}

    def test_parse_simple_dict(self):
        """Test parsing simple dict."""
        result = parse_applescript_dict('{name:"Test", id:"123"}')
        assert result.get("name") == "Test"
        assert result.get("id") == "123"
