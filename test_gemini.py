import os
from google import genai

# 2. 你的 API Key
API_KEY = "AIzaSyDsDuGWBerTCqo6-QQSHo3Vu1wmiy25hz4"

# 3. 使用全新的 genai SDK 初始化客户端
client = genai.Client(api_key=API_KEY)

print("正在呼叫 Gemini 大脑，请稍候...")

prompt = """
你是一个顶级的场景架构师。请提取下面这句话的核心视觉元素，
并输出一句极具画面感、适合用来生成图片的英文提示词 (Image Prompt)。

原文：阳光透过大教堂彩绘玻璃，洒在满是灰尘的古老魔法书上。
"""

try:
    # 4. 换用你截图里看到的最新 3.5 flash 模型
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
    )
    print("\n✅ === Gemini API 通信成功！===")
    print("AI 返回的生图提示词：")
    print(response.text)
except Exception as e:
    print("\n❌ 通信失败，错误信息：", e)
