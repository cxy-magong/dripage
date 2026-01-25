#!/usr/bin/env python
"""
Test concurrent get tool functionality.
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
import time


async def test_concurrent_get():
    """Test new get tool with concurrent formats."""
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

            # Test 2: Single format (markdown)
            print("\n=== Test 2: Single format (markdown) ===")
            start = time.time()
            try:
                result = await session.call_tool("get", {"url": "https://example.com", "formats": "markdown"})
                elapsed = time.time() - start
                print(f"Result: {result.content[0].text if result.content else 'No content'}")
                print(f"Time: {elapsed:.2f}s")
            except Exception as e:
                print(f"Error: {e}")

            # Test 3: Single format (string)
            print("\n=== Test 3: Single format (string 'html') ===")
            start = time.time()
            try:
                result = await session.call_tool("get", {"url": "https://example.com", "formats": "html"})
                elapsed = time.time() - start
                print(f"Result: {result.content[0].text if result.content else 'No content'}")
                print(f"Time: {elapsed:.2f}s")
            except Exception as e:
                print(f"Error: {e}")

            # Test 4: Multiple formats (markdown + html)
            print("\n=== Test 4: Multiple formats (markdown + html) ===")
            start = time.time()
            try:
                result = await session.call_tool("get", {"url": "https://example.com", "formats": ["markdown", "html"]})
                elapsed = time.time() - start
                print(f"Result: {result.content[0].text if result.content else 'No content'}")
                print(f"Time: {elapsed:.2f}s")
            except Exception as e:
                print(f"Error: {e}")

            # Test 5: All formats (concurrent)
            print("\n=== Test 5: All formats (concurrent) ===")
            start = time.time()
            try:
                result = await session.call_tool("get", {"url": "https://example.com", "formats": ["markdown", "html", "img", "mhtml"]})
                elapsed = time.time() - start
                print(f"Result: {result.content[0].text if result.content else 'No content'}")
                print(f"Time: {elapsed:.2f}s")
            except Exception as e:
                print(f"Error: {e}")

            # Test 6: Verify all files created
            print("\n=== Test 6: Verify created files ===")
            try:
                output_dir = project_dir / "output"
                recent_files = sorted(
                    [f for f in output_dir.glob("page_*") if f.is_file()],
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )[:5]

                print(f"Recent files in output/:")
                for f in recent_files:
                    size = f.stat().st_size
                    print(f"  - {f.name} ({size:,} bytes)")
            except Exception as e:
                print(f"Error: {e}")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_concurrent_get())
