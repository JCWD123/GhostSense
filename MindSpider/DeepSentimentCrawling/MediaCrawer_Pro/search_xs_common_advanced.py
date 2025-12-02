#!/usr/bin/env python3
"""
高级搜索：在已下载的JS文件中搜索 x-s-common 相关代码
"""
import re
from pathlib import Path

JS_DIR = Path("xhs_js_files")

# 更全面的搜索模式
PATTERNS = [
    # 直接搜索字符串
    (r'xsCommon', '函数名: xsCommon'),
    (r'X-S-Common', '请求头: X-S-Common'),
    (r'x-s-common', '请求头: x-s-common (小写)'),
    
    # JSON.stringify 相关
    (r'JSON\.stringify.*setRequestHeader', 'JSON.stringify + setRequestHeader'),
    (r'setRequestHeader.*X-S', 'setRequestHeader with X-S'),
    
    # 可能的混淆模式
    (r'["\']s0["\'].*["\']s1["\']', '参数对象: s0, s1 (签名参数)'),
    (r'["\']x0["\'].*["\']x1["\']', '参数对象: x0, x1'),
    (r'["\']x8["\'].*["\']x9["\']', '参数对象: x8, x9'),
    
    # Base64编码
    (r'btoa\([^)]+\)', 'Base64编码: btoa'),
    (r'atob\([^)]+\)', 'Base64解码: atob'),
    
    # 加密相关
    (r'\.encrypt\(', '加密方法'),
    (r'\.encode\(', '编码方法'),
    (r'\.sign\(', '签名方法'),
]


def search_in_files():
    """在所有JS文件中搜索"""
    if not JS_DIR.exists():
        print("❌ 目录不存在:", JS_DIR)
        return
    
    js_files = list(JS_DIR.glob("*.js"))
    
    if not js_files:
        print("❌ 没有找到JS文件")
        return
    
    print("=" * 80)
    print("🔍 高级搜索：x-s-common 相关代码")
    print("=" * 80)
    print(f"\n📂 搜索文件数: {len(js_files)}\n")
    
    total_found = 0
    
    for js_file in js_files:
        print(f"\n📄 文件: {js_file.name}")
        print("-" * 80)
        
        try:
            content = js_file.read_text(encoding='utf-8')
            file_found = 0
            
            for pattern, description in PATTERNS:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                
                if matches:
                    print(f"\n  🎯 找到: {description}")
                    print(f"     匹配数: {len(matches)}")
                    
                    # 显示前3个匹配的上下文
                    for i, match in enumerate(matches[:3], 1):
                        start = max(0, match.start() - 100)
                        end = min(len(content), match.end() + 100)
                        context = content[start:end]
                        
                        # 计算行号
                        line_num = content[:match.start()].count('\n') + 1
                        
                        print(f"     匹配 {i} (行 {line_num}):")
                        # 清理显示
                        context_clean = context.replace('\n', ' ')
                        if len(context_clean) > 150:
                            context_clean = context_clean[:150] + '...'
                        print(f"     {context_clean}")
                    
                    file_found += len(matches)
            
            if file_found > 0:
                print(f"\n  ✅ 本文件共找到 {file_found} 个匹配")
                total_found += file_found
            else:
                print("  ⚠️ 未找到匹配项")
                
        except Exception as e:
            print(f"  ❌ 读取失败: {e}")
    
    print("\n" + "=" * 80)
    print(f"📊 总结: 共找到 {total_found} 个匹配项")
    print("=" * 80)
    
    if total_found > 0:
        print("\n💡 下一步:")
        print("  1. 根据匹配的行号，在对应JS文件中查看完整代码")
        print("  2. 找到 xsCommon 函数的完整实现")
        print("  3. 找到 p.lz, p.xE, p.tb 的定义")
    else:
        print("\n💡 如果仍未找到，可能原因:")
        print("  1. 代码在其他JS文件中（需要下载更多文件）")
        print("  2. 变量名被完全混淆（如 a, b, c）")
        print("  3. 使用 WebAssembly 实现（需要逆向wasm）")


def extract_function_around_line(filename, target_line, before=20, after=20):
    """提取指定行周围的代码"""
    filepath = JS_DIR / filename
    
    if not filepath.exists():
        print(f"❌ 文件不存在: {filename}")
        return
    
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    start = max(0, target_line - before - 1)
    end = min(len(lines), target_line + after)
    
    print(f"\n{'=' * 80}")
    print(f"📄 文件: {filename}")
    print(f"📍 行号: {target_line} (上下文: -{before}/+{after})")
    print(f"{'=' * 80}\n")
    
    for i in range(start, end):
        marker = ">>> " if i == target_line - 1 else "    "
        print(f"{marker}{i+1:6d} | {lines[i]}")


if __name__ == "__main__":
    search_in_files()
    
    print("\n\n" + "=" * 80)
    print("🔧 辅助功能：提取指定行的代码")
    print("=" * 80)
    print("\n如果找到了关键匹配，可以运行:")
    print("  python -c \"from search_xs_common_advanced import extract_function_around_line; \\")
    print("             extract_function_around_line('index.5d840971.js', 1234, 30, 30)\"")





