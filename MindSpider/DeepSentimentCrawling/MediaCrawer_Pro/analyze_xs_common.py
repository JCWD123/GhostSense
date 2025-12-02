#!/usr/bin/env python3
"""
分析 x-s-common 的结构

从真实值反推可能的算法
"""
import base64
import binascii

# 真实的 x-s-common 值
XS_COMMON = "2UQAPsHC+aIjqArjwjHjNsQhPsHCH0rjNsQhPaHCH0c1Pjh9HjIj2eHjwjQgynEDJ74AHjIj2ePjwjQhyoPTqBPT49pjHjIj2ecjwjHFN0W9N0ZjNsQh+aHCH0rEG/DU+AP780b08n+kGnpSGdpiqfTh2gpUPASM2BEMqALIqBWAJ0YS+/ZIPeZUPeDI+0HjNsQh+jHCHjHVHdW7H0ijHjIj2eWjwjQQPAYUaBzdq9k6qB4Q4fpA8b878FSet9RQzLlTcSiM8/+n4MYP8F8LagY/P9Ql4FpUzfpS2BcI8nT1GFbC/L88JdbFyrSiafp/cDMra7pFLDDAa7+8J7QgabmFz7Qjp0mcwp4fanD68p40+fp8qgzELLbILrDA+9p3JpH9LLI3+LSk+d+DJfpSL98lnLYl49IUqgcMc0mrcDShtMmozBD6qM8FyFSh8o+h4g4U+obFyLSi4nbQz/+SPFlnPrDApSzQcA4SPopFJeQmzBMA/o8Szb+NqM+c4ApQzg8Ayp8FaDRl4AYs4g4fLomD8pzBpFRQ2ezLanSM+Skc47Qc4gcMag8VGLlj87PAqgzhagYSqAbn4FYQy7pTanTQ2npx87+8NM4L89L78p+l4BL6ze4AzB+IygmS8Bp8qDzFaLP98Lzn4AQQzLEAL7bFJBEVL7pwyS8Fag868nTl4e+0n04ApfuF8FSbL7SQyrpotASrpLS92dDFa/YOanS0+Mkc4FbQ4fSe+Bu6qFzP8oP9Lo4naLP78p+D+7+DPbHFaLp9qA+QzFMFpd4panSDqA+AN7+hnDESyp8FGf+p8np8pd4iag8Vqokm+fpDqg4eqBEtqFzn4MmQ2BlFagYyL9RM4FRdpd4Iq7HFyBppN9L9/o8Szbm7zDS987PlqfRAPLzyyLSk+7+xGfRAP94UzDSbPBLALoz9anSjLDRl4FROqgziagYSq7Yc4A4QyrbSpSmFyrSiN7+8qgz/z7b72nMc4FzQ4DS3a/+Q4ezYzMPFnaRSygpFyDSkJgQQzLRALM8F2DQ6zDF6wg8Sy0Sy4DSkzLEo4gzCqdpFJrS94fLALozp/7mN8nS0/d+kagkSanYdqA86+d+L4gzCqop7arS9+9LIpd4fanDM8/8x4gSQcFTA8B8O8Lzn4b+Q2B4A2op74/QfpFQQzpqFaL+dqM8++d+/8aRA8rD98p4M494QcFpGag8kpfbl49zQ2bmfanS68/bT+rMCqFkSp7pFJLSk2dQILo4QJpkS8nz+PBp8pdzI8Mm7nDSh4/FjNsQhwaHCN/LAPAW9+0WUPaIj2erIH0ilwsIj2erlH0ijJfRUJnbVHdF="

print("=" * 80)
print("🔬 x-s-common 结构分析")
print("=" * 80)

print(f"\n📊 基本信息:")
print(f"  长度: {len(XS_COMMON)} 字符")
print(f"  前缀: {XS_COMMON[:20]}")
print(f"  后缀: {XS_COMMON[-20:]}")

# 尝试Base64解码
print(f"\n🔓 尝试Base64解码:")
try:
    decoded = base64.b64decode(XS_COMMON)
    print(f"  ✅ 解码成功！")
    print(f"  解码后长度: {len(decoded)} 字节")
    print(f"  前20字节: {decoded[:20]}")
    print(f"  Hex: {decoded[:40].hex()}")
    
    # 尝试判断是否是加密数据
    print(f"\n🔍 数据特征:")
    
    # 计算熵（随机性）
    from collections import Counter
    byte_counts = Counter(decoded)
    entropy = -sum(count/len(decoded) * (count/len(decoded)).bit_length() for count in byte_counts.values())
    print(f"  熵值: {entropy:.2f} (越高越随机)")
    
    # 检查是否包含可打印字符
    printable = sum(1 for b in decoded if 32 <= b <= 126)
    print(f"  可打印字符比例: {printable/len(decoded)*100:.1f}%")
    
    # 查找重复模式
    print(f"\n🔍 查找重复模式:")
    for pattern_len in [2, 4, 8]:
        patterns = {}
        for i in range(len(decoded) - pattern_len):
            pattern = decoded[i:i+pattern_len].hex()
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        # 找出现3次以上的模式
        frequent = [(p, c) for p, c in patterns.items() if c >= 3]
        if frequent:
            frequent.sort(key=lambda x: x[1], reverse=True)
            print(f"  {pattern_len}字节模式 (前3个):")
            for pattern, count in frequent[:3]:
                print(f"    {pattern}: 出现{count}次")
    
    # 尝试查找特征字节序列
    print(f"\n🎯 特征分析:")
    
    # 检查是否有magic number
    magic = decoded[:4].hex()
    print(f"  Magic Number: 0x{magic}")
    
    # 检查是否有分隔符
    separators = [b'\x00', b'\x01', b'\x02', b'\xff', b'|', b',', b';']
    for sep in separators:
        count = decoded.count(sep)
        if count > 0:
            print(f"  分隔符 {sep.hex()}: 出现{count}次")
    
except Exception as e:
    print(f"  ❌ 解码失败: {e}")

# 分析字符分布
print(f"\n📊 字符分布:")
char_types = {
    '大写字母': sum(1 for c in XS_COMMON if c.isupper()),
    '小写字母': sum(1 for c in XS_COMMON if c.islower()),
    '数字': sum(1 for c in XS_COMMON if c.isdigit()),
    '特殊字符': sum(1 for c in XS_COMMON if c in '+/='),
}

for ctype, count in char_types.items():
    print(f"  {ctype}: {count} ({count/len(XS_COMMON)*100:.1f}%)")

# 查找固定前缀模式
print(f"\n🔍 重复子串分析:")
repeating = []
for substr_len in [4, 6, 8, 10]:
    seen = {}
    for i in range(len(XS_COMMON) - substr_len):
        substr = XS_COMMON[i:i+substr_len]
        if substr in seen:
            repeating.append((substr, seen[substr], i))
        seen[substr] = i

if repeating:
    print("  发现重复子串（前5个）:")
    for substr, pos1, pos2 in repeating[:5]:
        print(f"    '{substr}' 在位置 {pos1} 和 {pos2}")

# 输出逆向建议
print("\n" + "=" * 80)
print("🎯 逆向建议")
print("=" * 80)

print("""
基于分析结果，x-s-common 可能是：

1. ✅ Base64编码的二进制数据
2. 🔒 可能经过加密（高熵值）
3. 📦 可能包含多个字段拼接

下一步行动：

1️⃣ 在浏览器中搜索生成代码
   关键词：'x-s-common', 'XSCommon', 'commonSign'

2️⃣ 查找加密算法
   可能使用：AES, RC4, ChaCha20, 或自定义加密

3️⃣ 查找输入参数
   可能包含：URL, method, timestamp, nonce, cookie字段

4️⃣ 查找密钥来源
   可能硬编码在JS中，或从服务器动态获取

📖 参考文档：docs/x-s-common逆向实战指南.md
""")






