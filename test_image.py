from huggingface_hub import InferenceClient
import os
import ssl

# ==================== 黑客松终极掀桌子补丁 ====================
# 1. 强行把全系统走你的 Clash 7897 专线
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'

# 2. 核心补丁：直接修改 Python 全局默认 SSL 上下文，彻底关闭证书校验
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# 3. 强行屏蔽环境变量中的 CA 证书干扰
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'
# ============================================================


# 粘贴你的真实 Token (保留引号)
HF_TOKEN = "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"

# 初始化客户端
client = InferenceClient(
    model="stabilityai/sdxl-turbo",
    token=HF_TOKEN
)

prompt = "A close-up shot of an ancient, heavy leather-bound grimoire resting on a weathered stone pedestal inside a majestic, dim Gothic cathedral. A dramatic, brilliant beam of volumetric sunlight streams down from a high stained-glass window, casting a vibrant kaleidoscope of sapphire blue, ruby red, and golden light directly onto the dusty book. In the glowing light shaft, countless tiny golden dust motes are suspended and dancing. The magic book is slightly open, covered in a fine layer of silver dust, with faint, glowing arcane runes shimmering on its yellowed parchment pages. Ethereal atmosphere, cinematic lighting, photorealistic, hyper-detailed textures, 8k resolution, depth of field, Unreal Engine 5 render style. --ar 16:9 --v 6.0"


def generate_image(prompt_text):
    print("🚀 正在激活【全局 SSL 免疫通道】，通过 7897 强制出图...")
    try:
        image = client.text_to_image(prompt_text)
        image.save("output_magic_book.png")
        print("\n✅ === 【官方通道】生图成功！===")
        print("请在左侧文件列表里点击 output_magic_book.png 查看你的插画！")
    except Exception as e:
        print(f"\n❌ 调试型报错: {type(e).__name__} -> {e}")


generate_image(prompt)
