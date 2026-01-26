#!/usr/bin/env python
"""
Direct test script for MCP server tools via HTTP.
This bypasses mcporter to test if the tools are properly registered.
"""
import requests
import json
import time


class MCPTester:
    """Test MCP server tools directly via HTTP"""

    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.mcp_endpoint = f"{base_url}/mcp"

    def call_tool(self, tool_name, arguments=None):
        """Call an MCP tool via HTTP"""
        url = f"{self.mcp_endpoint}/tools/{tool_name}"
        payload = {"arguments": arguments or {}}

        try:
            print(f"\n📞 Calling: {tool_name}")
            print(f"   Arguments: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            # Parse response
            if response.headers.get('content-type') == 'application/json':
                result = response.json()
                print(f"   ✅ Success (JSON)")
                print(f"   Response:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
                return result
            else:
                print(f"   ✅ Success (Text)")
                print(f"   Response:\n{response.text[:500]}")
                return response.text

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON Parse Error: {e}")
            print(f"   Raw Response:\n{response.text[:500]}")
            return None

    def list_all_tools(self):
        """List all available tools"""
        print("\n" + "="*60)
        print("Listing all available MCP tools...")
        print("="*60)

        try:
            # Try tools/list endpoint
            response = requests.get(f"{self.mcp_endpoint}/tools/list", timeout=10)
            if response.status_code == 200:
                tools = response.json()
                print(f"\n✅ Found {len(tools)} tools:\n")
                for i, tool in enumerate(tools, 1):
                    name = tool.get('name', 'Unknown')
                    desc = tool.get('description', 'No description')
                    desc_short = desc[:80] + '...' if len(desc) > 80 else desc
                    print(f"  {i:2d}. {name}")
                    print(f"      {desc_short}")
                return tools
            else:
                print(f"❌ Failed to list tools: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error listing tools: {e}")
            return None

    def test_all_tools(self):
        """Test all tab management tools"""
        print("\n" + "="*60)
        print("Testing all tab management tools...")
        print("="*60)

        # Test 1: List tabs
        print("\n--- Test 1: List Tabs ---")
        self.call_tool("browser_list_tabs_tool")

        time.sleep(1)

        # Test 2: Get current tab info
        print("\n--- Test 2: Get Current Tab Info ---")
        self.call_tool("browser_get_current_tab_info_tool")

        time.sleep(1)

        # Test 3: Open new tab
        print("\n--- Test 3: Open New Tab ---")
        result = self.call_tool("browser_new_tab_tool", {"url": "https://www.baidu.com"})

        time.sleep(2)

        # Test 4: List tabs again
        print("\n--- Test 4: List Tabs (after new tab) ---")
        self.call_tool("browser_list_tabs_tool")

        time.sleep(1)

        # Test 5: Switch to first tab
        print("\n--- Test 5: Switch to Tab 0 ---")
        self.call_tool("browser_switch_tab_tool", {"tab_index": 0})

        time.sleep(1)

        # Test 6: Get current tab info after switch
        print("\n--- Test 6: Get Current Tab Info (after switch) ---")
        self.call_tool("browser_get_current_tab_info_tool")

        time.sleep(1)

        # Test 7: Close second tab
        print("\n--- Test 7: Close Tab 1 ---")
        self.call_tool("browser_close_tab_tool", {"tab_index": 1})

        time.sleep(1)

        # Test 8: List tabs after close
        print("\n--- Test 8: List Tabs (after close) ---")
        self.call_tool("browser_list_tabs_tool")

        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)


def main():
    """Main test function"""
    print("="*60)
    print("MCP Server Tab Management Tools Test")
    print("="*60)

    tester = MCPTester()

    # First, list all available tools
    tools = tester.list_all_tools()

    # Count tab-related tools
    if tools:
        tab_tools = [t for t in tools if 'tab' in t.get('name', '').lower()]
        print(f"\n📊 Found {len(tab_tools)} tab management tools:")
        for tool in tab_tools:
            print(f"   - {tool.get('name')}")

    # Run comprehensive tests
    tester.test_all_tools()


if __name__ == "__main__":
    main()
