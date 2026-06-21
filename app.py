import streamlit as st
import google.genai as genai
from google.genai import types
import urllib.parse
from PIL import Image

# 1. 网页基础配置（适配手机端屏幕）
st.set_page_config(
    page_title="VisionReader AI - 随身视界阅读器",
    page_icon="📖",
    layout="centered"
)

# 手机端精简标题
st.title("📖 VisionReader AI")
st.caption("移动端沉浸式阅读伴侣 - 拍照即画")

# 2. 侧边栏配置密钥与参数
with st.sidebar:
    st.header("⚙️ 核心配置")
    api_key = st.text_input("Gemini API Key", value="AIzaSyDsDuGWBerTCqo6-QQSHo3Vu1wmiy25hz4", type="password")
    st.markdown("---")
    st.info("💡 提示：当前模式已开启【Gemini 原生多模态视觉链路】，无需本地安装任何 OCR 识别库。")

# 初始化 Gemini 客户端
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.warning("请在侧边栏输入有效的 Gemini API Key")
    st.stop()

# 3. 核心拍照组件：在手机上打开会自动唤起后置摄像头
camera_file = st.camera_input("📸 拍下当前阅读的书页")

# 4. 如果用户拍了照，立刻自动触发全链路 Pipeline
if camera_file:
    # 将上传的文件转化为 PIL Image 对象
    img = Image.open(camera_file)

    # 在手机界面上展示刚刚拍下的照片（缩略图）
    with st.expander("👁️ 查看已捕获的书页快照", expanded=False):
        st.image(img, use_column_width=True)

    # 开启极具仪式感的动态加载条
    with st.status("🧠 视觉大脑正在解析书页意境...", expanded=True) as status:

        # 核心 Prompt：让 Gemini 同时扮演 OCR 识别器和场景架构师
        prompt = """
        你是一个顶级的场景架构师和文字识别专家。
        请仔细阅读这张图片中的所有中文字符，理解这页书的核心剧情、空间场景、氛围色彩和主体对象。
        然后，请为我输出一句极具电影感、视觉冲击力、适合用来生成图片的英文提示词 (Image Prompt)。
        
        注意：你只需要、且只能输出那句英文提示词本身，绝对不要包含任何多余的解释、标点或引言。
        """

        try:
            # 2026年最新多模态调用：直接将文本 Prompt 和图片对象 img 一起打包投递
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=[img, prompt]
            )

            generated_prompt = response.text.strip()

            st.write("✨ **Gemini 提炼的视觉灵魂剧本：**")
            st.code(generated_prompt, language="text")

            # 转换为 URL 编码，拼接到 Pollinations 极速渲染流中
            status.update(label="🎨 正在将意境同步渲染至手机画布...", state="running")
            encoded_prompt = urllib.parse.quote(generated_prompt)
            # 16:9 的电影宽屏尺寸，去除 logo
            final_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true"

            status.update(label="🎉 沉浸式视界已同步！", state="complete", expanded=False)

            # 5. 在手机正中心啪地展示渲染好的插画
            st.markdown("### 🖼️ 沉浸意境剧场")
            st.image(final_image_url, caption="当前页面的视觉具象化展现", use_column_width=True)

        except Exception as e:
            status.update(label="❌ 链路发生中断", state="error")
            st.error(f"全自动化渲染失败，请检查网络。错误信息：{e}")
