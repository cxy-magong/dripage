#!/usr/bin/env python
"""
Locate Element 示例 - 简洁版本

演示直接调用 locate_element 工具，打印原始结果和状态
"""

import os
import sys
from pathlib import Path
import json
from PIL import Image
# 添加项目目录到路径
project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from tools import locate_element as locate_element_tool
from tools.agent_tools import CoordinateConverter


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


def verify_coordinate_convert_box_with_runtime():
    """
    验证 coordinate_convert_box_with_runtime 的坐标转换是否正确

    参考 glm_4_1v_with_bbox_demo.log 中的转换结果：
    - 原始图像尺寸: 826 x 620
    - GLM 返回坐标: [460, 465, 578, 869] (基于 999x999)
    - 期望转换结果: [380, 288, 477, 539]
    """
    print("\n" + "="*80)
    print("验证 coordinate_convert_box_with_runtime")
    print("="*80)

    # 测试数据（从 glm_4_1v_with_bbox_demo.log 中提取）
    original_width = 826
    original_height = 620
    glm_box = [460, 465, 578, 869]
    expected_result = [380, 288, 477, 539]

    print(f"\n原始图像尺寸: {original_width} x {original_height}")
    print(f"GLM 返回坐标 (999x999): {glm_box}")
    print(f"期望转换结果: {expected_result}")

    # 使用 CoordinateConverter 进行转换
    converter = CoordinateConverter(original_width, original_height, None)
    actual_result = converter.convert_box(glm_box)

    print(f"\n实际转换结果: {actual_result}")
    print(f"\n转换公式:")
    print(f"  scale_x = {original_width} / 999 = {converter.scale_x:.6f}")
    print(f"  scale_y = {original_height} / 999 = {converter.scale_y:.6f}")
    print(f"\n详细计算:")
    print(f"  x1 = {glm_box[0]} * {converter.scale_x:.6f} = {glm_box[0] * converter.scale_x:.2f} -> {actual_result[0]}")
    print(f"  y1 = {glm_box[1]} * {converter.scale_y:.6f} = {glm_box[1] * converter.scale_y:.2f} -> {actual_result[1]}")
    print(f"  x2 = {glm_box[2]} * {converter.scale_x:.6f} = {glm_box[2] * converter.scale_x:.2f} -> {actual_result[2]}")
    print(f"  y2 = {glm_box[3]} * {converter.scale_y:.6f} = {glm_box[3] * converter.scale_y:.2f} -> {actual_result[3]}")

    # 验证结果
    print(f"\n验证结果:")
    if actual_result == expected_result:
        print(f"  ✅ PASSED - 转换结果与期望值一致")
        return True
    else:
        print(f"  ❌ FAILED - 转换结果与期望值不一致")
        print(f"  差异: {actual_result} vs {expected_result}")
        return False


def verify_coordinate_convert_point_with_runtime():
    """
    验证 coordinate_convert_point_with_runtime 的坐标转换是否正确

    使用相同的转换逻辑测试点坐标
    """
    print("\n" + "="*80)
    print("验证 coordinate_convert_point_with_runtime")
    print("="*80)

    # 测试数据
    original_width = 826
    original_height = 620
    glm_point = [519, 667]  # 使用 box 中心点计算: (460+578)/2=519, (465+869)/2=667

    # 计算期望结果
    converter = CoordinateConverter(original_width, original_height, None)
    expected_x = int(glm_point[0] * converter.scale_x)
    expected_y = int(glm_point[1] * converter.scale_y)
    expected_result = [expected_x, expected_y]

    print(f"\n原始图像尺寸: {original_width} x {original_height}")
    print(f"GLM 返回坐标 (999x999): {glm_point}")
    print(f"期望转换结果: {expected_result}")

    # 使用 CoordinateConverter 进行转换
    actual_result = converter.convert_point(glm_point)

    print(f"\n实际转换结果: {actual_result}")
    print(f"\n转换公式:")
    print(f"  scale_x = {original_width} / 999 = {converter.scale_x:.6f}")
    print(f"  scale_y = {original_height} / 999 = {converter.scale_y:.6f}")
    print(f"\n详细计算:")
    print(f"  x = {glm_point[0]} * {converter.scale_x:.6f} = {glm_point[0] * converter.scale_x:.2f} -> {actual_result[0]}")
    print(f"  y = {glm_point[1]} * {converter.scale_y:.6f} = {glm_point[1] * converter.scale_y:.2f} -> {actual_result[1]}")

    # 验证结果
    print(f"\n验证结果:")
    if actual_result == expected_result:
        print(f"  ✅ PASSED - 转换结果与期望值一致")
        return True
    else:
        print(f"  ❌ FAILED - 转换结果与期望值不一致")
        print(f"  差异: {actual_result} vs {expected_result}")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Locate Element 示例 - 简洁版")
    print("="*80)

    # 验证 box 坐标转换
    box_verify_result = verify_coordinate_convert_box_with_runtime()

    if not box_verify_result:
        print("\n⚠️  Box 坐标转换验证失败，需要修复 coordinate_convert_box_with_runtime\n")

    # 验证 point 坐标转换
    point_verify_result = verify_coordinate_convert_point_with_runtime()

    if not point_verify_result:
        print("\n⚠️  Point 坐标转换验证失败，需要修复 coordinate_convert_point_with_runtime\n")

    # 方式 1: 直接调用
    # example_direct_invoke()

    # 方式 2: 工具 invoke（仅在验证通过后运行）
    if box_verify_result and point_verify_result:
        print("\n" + "="*80)
        print("所有验证通过，运行 example_tool_invoke")
        print("="*80)
        example_tool_invoke()
    else:
        print("\n跳过 example_tool_invoke，先修复坐标转换问题\n")

    print("\n✅ 完成\n")
