#!/bin/bash
# 下载小红书关键JS文件并搜索 p.lz, p.xE, p.tb 函数

echo "🔍 开始下载和搜索小红书JS文件..."
echo ""

# 创建临时目录
mkdir -p xhs_js_files
cd xhs_js_files

# 关键JS文件URL列表
urls=(
    "https://fe-static.xhscdn.com/formula-static/xhs-pc-web/public/resource/js/index.5d840971.js"
    "https://fe-static.xhscdn.com/formula-static/xhs-pc-web/public/resource/js/vendor.b694e9bb.js"
    "https://fe-static.xhscdn.com/formula-static/xhs-pc-web/public/resource/js/async/Search.8169e1b6.js"
    "https://fe-static.xhscdn.com/as/v1/3e44/public/04b29480233f4def5c875875b6bdc3b1.js"
    "https://fe-static.xhscdn.com/formula-static/xhs-pc-web/public/resource/js/library-axios.2c978173.js"
)

# 下载文件
echo "📥 下载JS文件..."
for url in "${urls[@]}"; do
    filename=$(basename "$url")
    echo "  下载: $filename"
    curl -s "$url" -o "$filename"
done

echo ""
echo "🔍 搜索关键函数..."
echo ""

# 搜索函数
search_patterns=(
    'p\.lz'
    '\.lz:'
    '\.lz='
    'lz:function'
    'lz=function'
    'p\.xE'
    '\.xE:'
    '\.xE='
    'xE:function'
    'xE=function'
    'p\.tb'
    '\.tb:'
    '\.tb='
    'tb:function'
    'tb=function'
    'X-S-Common'
    'x-s-common'
)

for pattern in "${search_patterns[@]}"; do
    echo "🔎 搜索: $pattern"
    grep -n "$pattern" *.js 2>/dev/null | head -5
    echo ""
done

echo "✅ 搜索完成！"
echo ""
echo "📂 文件已保存到: xhs_js_files/"
echo "💡 如果找到了函数，可以手动查看对应文件"

cd ..







