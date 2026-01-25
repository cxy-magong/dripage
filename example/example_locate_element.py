#!/usr/bin/env python
"""
Locate Element 示例 - 简洁版本

演示直接调用 locate_element 工具，打印原始结果和状态
"""

import os
import sys
from pathlib import Path
import json 
# 添加项目目录到路径
project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from tools import locate_element as locate_element_tool


def example_direct_invoke():
    """直接调用 .func 方式"""
    print("\n" + "="*80)
    print("方式 1: 直接调用 locate_element.func")
    print("="*80)

    result = locate_element_tool.func(query="搜索输入框")

    print("\n📄 原始结果:")
    print(result)

    return result


def example_tool_invoke():
    """直接调用 locate_element.invoke()"""
    print("\n" + "="*80)
    print("方式 2: 直接调用 locate_element.invoke()")
    print("="*80)

    result = locate_element_tool.invoke({"query": "给出输入框的位置信息"})
    result_data = result.update
    
    print(f"\n🔍 结果 (JSON 格式):")
    print(json.dumps(result_data, ensure_ascii=False, indent=2))
    
    print(f"\n📄 结果 (字典格式):")
    print(result_data)
    
    # 访问具体字段
    if result_data.get('locate_element_result'):
        locate_result = result_data['locate_element_result']
        print(f"\n📊 定位结果详情:")
        print(f"  查询: {locate_result.get('query')}")
        print(f"  状态: {locate_result.get('status')}")
        
    print("\n� 原始结果对象:")
    print(result)

    return result


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Locate Element 示例 - 简洁版")
    print("="*80)

    # 方式 1: 直接调用
    # example_direct_invoke()

    # 方式 2: 工具 invoke
    example_tool_invoke()

    print("\n✅ 完成\n")
