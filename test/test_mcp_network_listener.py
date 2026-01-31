#!/usr/bin/env python
"""
Test script for network listener tools in MCP server via stdio.
"""
import asyncio
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_network_listener_via_mcp():
    """Test network listener tools via MCP server."""
    print("=" * 60)
    print("Testing Network Listener Tools via MCP Server")
    print("=" * 60)

    # Create server parameters
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "mcp_server.py"],
        cwd=str(project_dir),
        env={
            "PYTHONPATH": str(project_dir),
        }
    )

    print("\nConnecting to MCP server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # List available tools
            print("\n=== Listing Available Tools ===")
            tools = await session.list_tools()

            # Filter for network listener tools
            network_tools = [t for t in tools.tools if 'network' in t.name.lower()]
            print(f"\nFound {len(network_tools)} network listener tools:")
            for tool in network_tools:
                print(f"  - {tool.name}: {tool.description}")

            if not network_tools:
                print("\n❌ No network listener tools found!")
                return False

            print("\n✅ Network listener tools are available!")

            # Test start listener tool
            print("\n=== Testing network_start_listener_tool ===")
            try:
                result = await session.call_tool(
                    "network_start_listener_tool",
                    {
                        "mimeType": "application/json",
                        "url_include": ".",
                        "refresh": False
                    }
                )
                print(f"Result:\n{result.content[0].text if result.content else 'No content'}")
            except Exception as e:
                print(f"❌ Error calling network_start_listener_tool: {e}")
                import traceback
                traceback.print_exc()

            # Test get listener data
            print("\n=== Testing network_get_listener_data_tool ===")
            try:
                result = await session.call_tool("network_get_listener_data_tool", {})
                print(f"Result:\n{result.content[0].text if result.content else 'No content'}")
            except Exception as e:
                print(f"❌ Error calling network_get_listener_data_tool: {e}")

            # Test stop listener
            print("\n=== Testing network_stop_listener_tool ===")
            try:
                result = await session.call_tool(
                    "network_stop_listener_tool",
                    {
                        "clear_data": True
                    }
                )
                print(f"Result:\n{result.content[0].text if result.content else 'No content'}")
            except Exception as e:
                print(f"❌ Error calling network_stop_listener_tool: {e}")

            # Test clear data
            print("\n=== Testing network_clear_listener_data_tool ===")
            try:
                result = await session.call_tool("network_clear_listener_data_tool", {})
                print(f"Result:\n{result.content[0].text if result.content else 'No content'}")
            except Exception as e:
                print(f"❌ Error calling network_clear_listener_data_tool: {e}")

    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_network_listener_via_mcp())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
