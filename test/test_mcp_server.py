#!/usr/bin/env python
"""
Test script for Dripage MCP server.
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


async def test_mcp_server():
    """Test the MCP server connection and tools."""
    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env={
            "PYTHONPATH": str(project_dir),
        }
    )

    print("Connecting to MCP server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # List available tools
            print("\n=== Available Tools ===")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Test screenshot tool
            print("\n=== Testing Screenshot Tool ===")
            try:
                result = await session.call_tool("screenshot", {})
                print(f"Result: {result.content[0].text if result.content else 'No content'}")
            except Exception as e:
                print(f"Error calling screenshot: {e}")

            # Test get tool
            print("\n=== Testing Get Tool ===")
            try:
                result = await session.call_tool("get", {"url": "https://example.com"})
                print(f"Result: {result.content[0].text}")
            except Exception as e:
                print(f"Error calling get: {e}")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
