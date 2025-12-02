#!/usr/bin/env python3
"""
自动下载小红书JS文件并搜索 p.lz, p.xE, p.tb 三个关键函数
"""
import os
import re
import asyncio
import httpx
from pathlib import Path

# 关键JS文件URL
JS_URLS = [
    "https://fe-static.xhscdn.com/formula-static/xhs-pc-web/public/resource/js/index.5d840971.js",
    "https://fe-static.xhscdn.com/formula-static/xhs-pc-web/public/resource/js/vendor.b694e9bb.js",
    "https://fe-static.xhscdn.com/formula-static/xhs-pc-web/public/resource/js/async/Search.8169e1b6.js",
    "https://fe-static.xhscdn.com/as/v1/3e44/public/04b29480233f4def5c875875b6bdc3b1.js",
    "https://fe-static.xhscdn.com/formula-static/xhs-pc-web/public/resource/js/library-axios.2c978173.js",
]

# 搜索模式
SEARCH_PATTERNS = [
    (r'\.lz\s*[:=]\s*function', 'p.lz 函数定义'),
    (r'lz:\s*function\s*\([^)]*\)\s*\{', 'lz 对象方法'),
    (r'\.xE\s*[:=]\s*function', 'p.xE 函数定义'),
    (r'xE:\s*function\s*\([^)]*\)\s*\{', 'xE 对象方法'),
    (r'\.tb\s*[:=]\s*function', 'p.tb 函数定义'),
    (r'tb:\s*function\s*\([^)]*\)\s*\{', 'tb 对象方法'),
    (r'["\'](X-S-Common|x-s-common)["\']', 'X-S-Common 字符串'),
]

OUTPUT_DIR = Path("xhs_js_files")


async def download_file(url: str, session: httpx.AsyncClient):
    """下载单个JS文件"""
    filename = url.split('/')[-1]
    filepath = OUTPUT_DIR / filename
    
    try:
        print(f"  📥 下载: {filename}")
        response = await session.get(url, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return filename, response.text
    except Exception as e:
        print(f"  ❌ 下载失败 {filename}: {e}")
        return filename, None


async def download_all_files():
    """下载所有JS文件"""
    print("📥 开始下载JS文件...\n")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    async with httpx.AsyncClient() as session:
        tasks = [download_file(url, session) for url in JS_URLS]
        results = await asyncio.gather(*tasks)
    
    return {name: content for name, content in results if content}


def search_in_file(filename: str, content: str):
    """在文件中搜索关键模式"""
    found = []
    
    for pattern, description in SEARCH_PATTERNS:
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        
        if matches:
            for match in matches[:3]:  # 最多显示3个匹配
                # 获取匹配位置的上下文
                start = max(0, match.start() - 200)
                end = min(len(content), match.end() + 200)
                context = content[start:end]
                
                # 计算行号
                line_num = content[:match.start()].count('\n') + 1
                
                found.append({
                    'file': filename,
                    'description': description,
                    'line': line_num,
                    'match': match.group(),
                    'context': context
                })
    
    return found


def extract_function_body(content: str, start_pos: int, max_length=5000):
    """提取函数体（简单版本，基于大括号匹配）"""
    brace_count = 0
    in_function = False
    func_start = start_pos
    
    for i in range(start_pos, min(start_pos + max_length, len(content))):
        char = content[i]
        
        if char == '{':
            if not in_function:
                in_function = True
                func_start = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if in_function and brace_count == 0:
                return content[func_start:i+1]
    
    return None


async def main():
    print("=" * 80)
    print("🔬 小红书 x-s-common 关键函数搜索工具")
    print("=" * 80)
    print()
    
    # 下载文件
    files = await download_all_files()
    
    if not files:
        print("\n❌ 没有成功下载任何文件")
        return
    
    print(f"\n✅ 成功下载 {len(files)} 个文件\n")
    
    # 搜索
    print("🔍 搜索关键函数...\n")
    print("=" * 80)
    
    all_results = []
    
    for filename, content in files.items():
        results = search_in_file(filename, content)
        all_results.extend(results)
    
    if not all_results:
        print("❌ 未找到任何匹配项")
        print("\n💡 建议：")
        print("  1. 函数可能被高度混淆")
        print("  2. 尝试手动在文件中搜索 'xsCommon'")
        print("  3. 查看已下载的文件: xhs_js_files/")
        return
    
    # 按文件分组显示结果
    from collections import defaultdict
    results_by_file = defaultdict(list)
    for result in all_results:
        results_by_file[result['file']].append(result)
    
    for filename, results in results_by_file.items():
        print(f"\n📄 文件: {filename}")
        print("-" * 80)
        
        for i, result in enumerate(results, 1):
            print(f"\n  🎯 匹配 {i}: {result['description']}")
            print(f"     行号: {result['line']}")
            print(f"     匹配: {result['match'][:100]}")
            print(f"     上下文预览:")
            
            # 显示上下文（截断）
            context = result['context'].replace('\n', ' ')
            if len(context) > 200:
                context = context[:200] + '...'
            print(f"     {context}")
    
    # 保存详细结果到文件
    output_file = OUTPUT_DIR / "search_results.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("小红书 x-s-common 函数搜索结果\n")
        f.write("=" * 80 + "\n\n")
        
        for result in all_results:
            f.write(f"文件: {result['file']}\n")
            f.write(f"描述: {result['description']}\n")
            f.write(f"行号: {result['line']}\n")
            f.write(f"匹配: {result['match']}\n")
            f.write(f"上下文:\n{result['context']}\n")
            f.write("-" * 80 + "\n\n")
    
    print("\n" + "=" * 80)
    print(f"✅ 搜索完成！共找到 {len(all_results)} 个匹配项")
    print(f"📁 详细结果已保存到: {output_file}")
    print(f"📂 JS文件保存在: {OUTPUT_DIR}/")
    print("=" * 80)
    
    print("\n💡 下一步：")
    print("  1. 查看 search_results.txt 中的详细结果")
    print("  2. 根据行号在对应JS文件中查看完整函数")
    print("  3. 复制函数代码进行分析")


if __name__ == "__main__":
    asyncio.run(main())






