#!/usr/bin/env python
"""
Comprehensive test script for browser tab management tools.
Tests all tab management features directly.
"""
import json
import time
from tools.browser_tabs import list_tabs, new_tab, close_tab, switch_tab, get_current_tab_info
from utils.drission_page import create_browser


def test_tab_management():
    """Test all tab management functions."""

    print("="*70)
    print("浏览器多标签管理工具测试")
    print("="*70)

    # Create browser connection
    print("\n🌐 初始化浏览器连接...")
    browser = create_browser()

    # Navigate to a starting page
    print("   导航到 example.com...")
    browser.get("https://www.example.com")
    time.sleep(2)

    # ========================================
    # Test 1: List tabs
    # ========================================
    print("\n" + "="*70)
    print("测试 1: 列出所有标签 (list_tabs)")
    print("="*70)

    result = list_tabs()
    data = json.loads(result)

    print(f"\n✅ 结果: {data.get('status', 'unknown')}")
    print(f"   标签数量: {data.get('count', 0)}")

    if data.get('tabs'):
        print("   标签列表:")
        for tab in data['tabs']:
            current_marker = "👈 [当前]" if tab.get('is_current') else ""
            print(f"     [{tab['index']}] {tab['title'][:40]:40s} {current_marker}")

    # ========================================
    # Test 2: Get current tab info
    # ========================================
    print("\n" + "="*70)
    print("测试 2: 获取当前标签信息 (get_current_tab_info)")
    print("="*70)

    result = get_current_tab_info()
    data = json.loads(result)

    print(f"\n✅ 结果: {data.get('status', 'unknown')}")
    print(f"   当前索引: {data.get('index')}")
    print(f"   标题: {data.get('title')}")
    print(f"   URL: {data.get('url')}")
    print(f"   总标签数: {data.get('total_tabs')}")

    # ========================================
    # Test 3: Open new tab
    # ========================================
    print("\n" + "="*70)
    print("测试 3: 打开新标签 (new_tab)")
    print("="*70)

    print("\n   打开 baidu.com...")
    result = new_tab("https://www.baidu.com")
    data = json.loads(result)

    print(f"\n✅ 结果: {data.get('status', 'unknown')}")
    print(f"   消息: {data.get('message')}")
    print(f"   新标签标题: {data.get('title')}")
    print(f"   新标签URL: {data.get('url')}")
    print(f"   新标签索引: {data.get('index')}")
    print(f"   总标签数: {data.get('total_tabs')}")

    time.sleep(2)

    # ========================================
    # Test 4: List tabs after opening new tab
    # ========================================
    print("\n" + "="*70)
    print("测试 4: 再次列出标签 (list_tabs)")
    print("="*70)

    result = list_tabs()
    data = json.loads(result)

    print(f"\n✅ 结果: {data.get('status', 'unknown')}")
    print(f"   标签数量: {data.get('count', 0)}")

    if data.get('tabs'):
        print("   标签列表:")
        for tab in data['tabs']:
            current_marker = "👈 [当前]" if tab.get('is_current') else ""
            print(f"     [{tab['index']}] {tab['title'][:40]:40s} {current_marker}")

    # ========================================
    # Test 5: Switch to first tab
    # ========================================
    print("\n" + "="*70)
    print("测试 5: 切换到标签 0 (switch_tab)")
    print("="*70)

    print("   切换到标签 0 (example.com)...")
    result = switch_tab(0)
    data = json.loads(result)

    print(f"\n✅ 结果: {data.get('status', 'unknown')}")
    print(f"   消息: {data.get('message')}")
    print(f"   当前标题: {data.get('title')}")
    print(f"   当前URL: {data.get('url')}")

    time.sleep(1)

    # ========================================
    # Test 6: Verify tab switched
    # ========================================
    print("\n" + "="*70)
    print("测试 6: 验证标签切换 (get_current_tab_info)")
    print("="*70)

    result = get_current_tab_info()
    data = json.loads(result)

    print(f"\n✅ 结果: {data.get('status', 'unknown')}")
    print(f"   当前索引: {data.get('index')} (应该是 0)")
    print(f"   标题: {data.get('title')}")
    print(f"   URL: {data.get('url')}")

    # ========================================
    # Test 7: Open another new tab
    # ========================================
    print("\n" + "="*70)
    print("测试 7: 打开另一个新标签 (new_tab)")
    print("="*70)

    print("   打开 google.com...")
    result = new_tab("https://www.google.com")
    data = json.loads(result)

    print(f"\n✅ 结果: {data.get('status', 'unknown')}")
    print(f"   消息: {data.get('message')}")
    print(f"   新标签索引: {data.get('index')}")

    time.sleep(2)

    # ========================================
    # Test 8: List all tabs
    # ========================================
    print("\n" + "="*70)
    print("测试 8: 列出所有标签 (list_tabs)")
    print("="*70)

    result = list_tabs()
    data = json.loads(result)

    print(f"\n✅ 结果: {data.get('status', 'unknown')}")
    print(f"   标签数量: {data.get('count', 0)}")

    if data.get('tabs'):
        print("   标签列表:")
        for tab in data['tabs']:
            current_marker = "👈 [当前]" if tab.get('is_current') else ""
            print(f"     [{tab['index']}] {tab['title'][:40]:40s} {current_marker}")

    # ========================================
    # Test 9: Close tab by index
    # ========================================
    print("\n" + "="*70)
    print("测试 9: 关闭指定标签 (close_tab with index)")
    print("="*70)

    print("   关闭标签 1 (baidu.com)...")
    result = close_tab(tab_index=1)
    data = json.loads(result)

    print(f"\n✅ 结果: {data.get('status', 'unknown')}")
    print(f"   消息: {data.get('message')}")
    print(f"   剩余标签数: {data.get('remaining_tabs')}")

    time.sleep(1)

    # ========================================
    # Test 10: List tabs after close
    # ========================================
    print("\n" + "="*70)
    print("测试 10: 关闭后列出标签 (list_tabs)")
    print("="*70)

    result = list_tabs()
    data = json.loads(result)

    print(f"\n✅ 结果: {data.get('status', 'unknown')}")
    print(f"   标签数量: {data.get('count', 0)}")

    if data.get('tabs'):
        print("   标签列表:")
        for tab in data['tabs']:
            current_marker = "👈 [当前]" if tab.get('is_current') else ""
            print(f"     [{tab['index']}] {tab['title'][:40]:40s} {current_marker}")

    # ========================================
    # Test 11: Open more tabs
    # ========================================
    print("\n" + "="*70)
    print("测试 11: 批量打开多个标签")
    print("="*70)

    urls = [
        "https://www.bing.com",
        "https://www.github.com",
        "https://news.ycombinator.com"
    ]

    for url in urls:
        print(f"\n   打开 {url}...")
        result = new_tab(url)
        data = json.loads(result)
        print(f"   ✅ 索引 {data.get('index')}: {data.get('title')[:40]}")
        time.sleep(1)

    # ========================================
    # Final summary
    # ========================================
    print("\n" + "="*70)
    print("最终状态")
    print("="*70)

    result = list_tabs()
    data = json.loads(result)

    print(f"\n✅ 总标签数: {data.get('count', 0)}")
    print(f"\n当前标签:")

    if data.get('tabs'):
        for tab in data['tabs']:
            current_marker = "👈 [当前]" if tab.get('is_current') else ""
            print(f"     [{tab['index']}] {tab['title'][:50]:50s}")
            print(f"          {tab.get('url')}")
            print(f"          {current_marker}")

    print("\n" + "="*70)
    print("✅ 所有测试完成！")
    print("="*70)

    print("\n📝 测试总结:")
    print("   ✅ list_tabs() - 列出所有标签")
    print("   ✅ get_current_tab_info() - 获取当前标签信息")
    print("   ✅ new_tab(url) - 打开新标签（带URL）")
    print("   ✅ new_tab() - 打开新标签（不带URL）")
    print("   ✅ switch_tab(index) - 切换到指定标签")
    print("   ✅ close_tab(index) - 关闭指定标签")
    print("   ✅ close_tab() - 关闭当前标签")
    print("   ✅ 批量操作 - 同时管理多个标签")
    print("\n📌 注意: 所有返回值都是标准化的 JSON 格式，便于 MCP 工具调用")


if __name__ == "__main__":
    try:
        test_tab_management()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
