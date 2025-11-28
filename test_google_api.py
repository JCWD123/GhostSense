import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

def test_google_api_connectivity():
    """
    测试 Google API (Gemini via OpenAI compatibility) 的连通性
    """
    print("=== 开始测试 Google API 连通性 ===")
    
    # 从环境变量获取配置
    api_key = os.getenv("INSIGHT_ENGINE_API_KEY", "AIzaSyB-HY2AzpNlK1MrIo9PXvRoF7ZOm3oX3vg")
    base_url = os.getenv("INSIGHT_ENGINE_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
    # 强制使用 gemini-2.0-flash 进行测试
    model_name = "gemini-2.0-flash"

    print(f"API KEY: {api_key[:8]}...{api_key[-4:]}")
    print(f"Base URL: {base_url}")
    print(f"Model: {model_name}")

    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        print("\n正在获取可用模型列表...")
        try:
            models = client.models.list()
            print("可用模型:")
            for model in models:
                print(f"- {model.id}")
        except Exception as list_err:
            print(f"无法列出模型: {list_err}")

        print("\n正在发送测试请求...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, simply reply 'Connection Successful!' if you receive this message."}
            ],
            max_tokens=20
        )

        print("\nRaw Response:")
        print(response)
        content = response.choices[0].message.content
        print(f"\n[SUCCESS] Test Passed! API Response: \n{content}")
        return True

    except Exception as e:
        print(f"\n[FAILURE] Test Failed! Error: \n{str(e)}")
        print("\n可能的原因:")
        print("1. 网络连接问题（需要科学上网？）")
        print("2. API Key 无效")
        print("3. Base URL 配置错误")
        print("4. 模型名称错误")
        return False

if __name__ == "__main__":
    test_google_api_connectivity()

