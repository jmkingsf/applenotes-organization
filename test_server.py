#!/usr/bin/env python3
"""Test script to verify the MCP server works correctly."""

import sys

def test_import():
    """Test that the server can be imported."""
    try:
        from applenotes_organization.server import mcp
        print("✅ Server imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import server: {e}")
        return False


def test_tools():
    """Test that tools are registered."""
    try:
        from applenotes_organization.server import mcp
        tools = list(mcp._local_provider._tools.keys())
        print(f"✅ Found {len(tools)} tools registered")
        print(f"   Tools: {', '.join(sorted(tools)[:5])}...")
        return len(tools) > 0
    except Exception as e:
        print(f"❌ Failed to list tools: {e}")
        return False


def main():
    """Run all tests."""
    print("Testing applenotes-organization MCP server...\n")
    
    results = []
    results.append(test_import())
    results.append(test_tools())
    
    print("\n" + "="*50)
    if all(results):
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
