#!/usr/bin/env python3
"""
批量缩小 JSON 文件中指定字段的值（数值型）。

用法示例：
    # 将所有以 "price" 结尾的字段值缩小 10 倍
    python json_scale_down.py input.json -o output.json -s price -m suffix -f 10

    # 将所有以 "id" 开头的字段值缩小 100 倍
    python json_scale_down.py input.json -o output.json -p id -m prefix -f 100

    # 直接覆盖原文件（谨慎使用）
    python json_scale_down.py input.json -i -s _value -m suffix -f 10
"""

import json
import argparse
import sys
from typing import Any, Dict, List, Union

def scale_value(value: Any, factor: float) -> Any:
    """如果 value 是数字，则除以 factor；否则原样返回。"""
    if isinstance(value, (int, float)):
        return value / factor
    return value

def process_node(node: Any, match_key: str, mode: str, factor: float) -> Any:
    """
    递归处理 JSON 节点。
    :param node: 当前处理的子结构（dict, list, 基本类型）
    :param match_key: 用于匹配的字符串
    :param mode: 'prefix' 或 'suffix'
    :param factor: 缩小的倍数（除以该数）
    :return: 处理后的节点
    """
    if isinstance(node, dict):
        new_dict = {}
        for k, v in node.items():
            # 检查键是否匹配
            matched = False
            if mode == 'prefix':
                matched = k.startswith(match_key)
            elif mode == 'suffix':
                matched = k.endswith(match_key)
            else:
                raise ValueError(f"不支持的匹配模式: {mode}，请使用 'prefix' 或 'suffix'")

            if matched:
                # 对该字段的值进行缩放
                new_dict[k] = scale_value(v, factor)
            else:
                # 递归处理子结构
                new_dict[k] = process_node(v, match_key, mode, factor)
        return new_dict
    elif isinstance(node, list):
        return [process_node(item, match_key, mode, factor) for item in node]
    else:
        # 基本类型（字符串、数字、布尔、null）不做处理
        return node

def main():
    parser = argparse.ArgumentParser(
        description="批量缩小 JSON 文件中匹配指定前缀/后缀的字段值。"
    )
    parser.add_argument("input", help="输入的 JSON 文件路径")
    parser.add_argument("-o", "--output", help="输出 JSON 文件路径（若不指定，则打印到标准输出）")
    parser.add_argument("-i", "--inplace", action="store_true",
                        help="直接覆盖输入文件（需谨慎，会丢失原文件）")
    parser.add_argument("-p", "--prefix", help="匹配字段前缀（与 --suffix 二选一）")
    parser.add_argument("-s", "--suffix", help="匹配字段后缀（与 --prefix 二选一）")
    parser.add_argument("-m", "--mode", choices=["prefix", "suffix"], required=True,
                        help="匹配模式：prefix（前缀）或 suffix（后缀）")
    parser.add_argument("-f", "--factor", type=float, default=10.0,
                        help="缩小倍数（默认 10），字段值会除以该数")

    args = parser.parse_args()

    # 校验匹配字符串
    if args.mode == "prefix" and not args.prefix:
        parser.error("当模式为 prefix 时，必须通过 -p/--prefix 指定前缀字符串")
    if args.mode == "suffix" and not args.suffix:
        parser.error("当模式为 suffix 时，必须通过 -s/--suffix 指定后缀字符串")

    match_key = args.prefix if args.mode == "prefix" else args.suffix

    # 读取 JSON
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取文件失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 处理
    try:
        result = process_node(data, match_key, args.mode, args.factor)
    except Exception as e:
        print(f"处理过程中出错: {e}", file=sys.stderr)
        sys.exit(1)

    # 输出
    output_json = json.dumps(result, indent=2, ensure_ascii=False)
    if args.inplace:
        # 覆盖原文件
        with open(args.input, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"已原地更新文件: {args.input}")
    elif args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"结果已写入: {args.output}")
    else:
        print(output_json)

if __name__ == "__main__":
    main()