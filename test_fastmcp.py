"""Test FastMCP API to understand correct usage."""

from fastmcp import FastMCP

# Create server
mcp = FastMCP("test-server")

# Test 1: Simple tool
@mcp.tool()
def simple_tool(message: str) -> str:
    """A simple test tool."""
    return f"Echo: {message}"

# Test 2: Tool with description
@mcp.tool(description="A tool that adds two numbers")
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    print("FastMCP test server created successfully!")
    print("Starting server...")
    mcp.run()
