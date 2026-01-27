#!/usr/bin/env python
"""
Test new get tool functionality.
"""
import asyncio
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_get_tool():
    """Test the new get tool with various formats."""
    # Create server parameters
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "mcp_server.py"],
        env={
            "PYTHONPATH": str(project_dir),
        }
    )

    print("Connecting to MCP server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # Test 1: Get current page info (no URL)
            print("\n=== Test 1: Get current page info (no URL) ===")
            try:
                result = await session.call_tool("get", {})
                print(f"Result: {result.content[0].text if result.content else 'No content'}")
            except Exception as e:
                print(f"Error: {e}")

            # Test 2: Get page as markdown
            print("\n=== Test 2: Get page as markdown ===")
            try:
                result = await session.call_tool("get", {"url": "https://example.com", "format": "markdown"})
                print(f"Result: {result.content[0].text if result.content else 'No content'}")
            except Exception as e:
                print(f"Error: {e}")

            # Test 3: Get page as HTML
            print("\n=== Test 3: Get page as HTML ===")
            try:
                result = await session.call_tool("get", {"url": "https://example.com", "format": "html"})
                print(f"Result: {result.content[0].text if result.content else 'No content'}")
            except Exception as e:
                print(f"Error: {e}")

            # Test 4: Get page as image
            print("\n=== Test 4: Get page as image ===")
            try:
                result = await session.call_tool("get", {"url": "https://example.com", "format": "img"})
                print(f"Result: {result.content[0].text if result.content else 'No content'}")
            except Exception as e:
                print(f"Error: {e}")

            # Test 5: Get page as mhtml
            print("\n=== Test 5: Get page as mhtml ===")
            try:
                result = await session.call_tool("get", {"url": "https://example.com", "format": "mhtml"})
                print(f"Result: {result.content[0].text if result.content else 'No content'}")
            except Exception as e:
                print(f"Error: {e}")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_get_tool())
