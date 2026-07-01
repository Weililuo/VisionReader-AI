"""
============================================================
VisionReader AI · 随身视界阅读器  v4.0 极简重构
高清上传 → 纯中文 OCR → 直连 Pollinations 生图
============================================================
"""

import streamlit as st
import google.genai as genai
from google.genai import types
import urllib.parse
from PIL import Image
import json
import io
import hashlib
import random

# ============================================================
# 🔐 核心配置
# ============================================================
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = str(st.secrets["GEMINI_API_KEY"]).strip()
else:
    GEMINI_API_KEY = ""

GEMINI_MODEL = "gemini-2.5-flash"

# Pollinations 固定画质后缀（确定性生图，不经过 AI 脑补）
STYLE_SUFFIX = ", masterpiece, highly detailed, cinematic lighting, 8K"

# ============================================================
# 📱 Streamlit 页面配置
# ============================================================
st.set_page_config(
    page_title="VisionReader AI · 视界阅读",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "VisionReader AI — 拍下书页，看见故事",
    },
)

if not GEMINI_API_KEY:
    st.error(
        "未配置 Gemini API Key。请在 `.streamlit/secrets.toml`（本地）"
        "或 Streamlit Cloud Secrets 中添加 `GEMINI_API_KEY`。"
    )
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# ============================================================
# 🧠 会话状态初始化
# ============================================================
if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0
if "img_hash" not in st.session_state:
    st.session_state.img_hash = ""
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""
if "final_image_url" not in st.session_state:
    st.session_state.final_image_url = ""
if "show_results" not in st.session_state:
    st.session_state.show_results = False
if "img_bytes" not in st.session_state:
    st.session_state.img_bytes = None
if "img_width" not in st.session_state:
    st.session_state.img_width = 0
if "img_height" not in st.session_state:
    st.session_state.img_height = 0

# ============================================================
# 🎨 极简现代暗色主题 CSS — 无动画、无炫技、纯净舒展
# ============================================================
st.markdown(
    """
<style>
    /* 全局暗色基底 */
    .stApp {
        background: #0a0a15;
    }

    /* 隐藏无关 chrome */
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    header[data-testid="stHeader"] { background: transparent !important; }

    /* 主容器全宽舒展 */
    .main .block-container {
        max-width: 900px !important;
        padding: 2rem 1.5rem 3rem !important;
    }

    /* 品牌标题 */
    h1 {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #e0e0f0 !important;
        text-align: center;
        letter-spacing: 0.04em;
        margin-bottom: 0.3rem !important;
        padding-top: 1rem !important;
    }

    /* 副标题 */
    .subtitle {
        text-align: center;
        color: #6a6a8a;
        font-size: 0.82rem;
        margin-bottom: 2.2rem;
        letter-spacing: 0.06em;
    }

    /* 上传提示大字 */
    .upload-hint {
        text-align: center;
        color: #a0a0c0;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        line-height: 1.8;
    }

    /* 文件上传器 — 巨型高亮 */
    [data-testid="stFileUploadDropzone"] {
        border-radius: 16px !important;
        border: 2px dashed rgba(139, 92, 246, 0.4) !important;
        padding: 2.5rem 1.5rem !important;
        background: rgba(139, 92, 246, 0.04) !important;
        transition: border-color 0.2s, background 0.2s !important;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: rgba(139, 92, 246, 0.7) !important;
        background: rgba(139, 92, 246, 0.07) !important;
    }

    /* 结果卡片 */
    .result-card {
        background: rgba(20, 20, 40, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 1.2rem;
        margin: 0.6rem 0;
    }

    /* OCR 文本框 */
    .ocr-area textarea {
        background: rgba(15, 15, 30, 0.5) !important;
        border: 1px solid rgba(96, 165, 250, 0.18) !important;
        border-radius: 12px !important;
        color: #d0d0e8 !important;
        font-size: 0.9rem !important;
        line-height: 1.8 !important;
        padding: 0.8rem !important;
    }

    /* 生图展示 — 全宽震撼 */
    .stImage img {
        border-radius: 14px !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5) !important;
    }

    /* 按钮 */
    .stButton > button {
        border-radius: 30px !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* 展开面板 */
    .streamlit-expanderHeader {
        border-radius: 12px !important;
        background: rgba(20, 20, 40, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        font-size: 0.82rem !important;
    }

    /* 状态组件 */
    .stStatus {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        background: rgba(15, 15, 30, 0.4) !important;
    }

    /* 分割线 */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
        margin: 1.6rem 0 !important;
    }

    /* 底部 */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.1);
        font-size: 0.64rem;
        padding: 2.5rem 0 0.5rem;
        letter-spacing: 0.05em;
    }

    /* 滚动条 */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.2);
        border-radius: 8px;
    }

    /* 胶囊标签 */
    .chip {
        display: inline-block;
        padding: 0.22rem 0.7rem;
        border-radius: 50px;
        font-size: 0.66rem;
        letter-spacing: 0.05em;
        margin-bottom: 0.6rem;
        font-weight: 600;
    }
    .chip.ocr  { background: rgba(96,165,250,0.1);  border:1px solid rgba(96,165,250,0.2);  color:#93c5fd; }
    .chip.art  { background: rgba(52,211,153,0.1);  border:1px solid rgba(52,211,153,0.18); color:#34d399; }

    /* 移动端适配 */
    @media (max-width: 640px) {
        .main .block-container {
            padding: 1rem 1rem 3rem !important;
        }
        h1 {
            font-size: 1.5rem !important;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 🏠 品牌头部
# ============================================================
st.markdown(
    """
<h1>📖 VisionReader AI</h1>
<p class="subtitle">拍下书页 · 看见故事 · 沉浸意境</p>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 📤 唯一上传区 — 巨型、直观、原生相机/相册
# ============================================================
st.markdown(
    '<p class="upload-hint">'
    '📸 点击下方按钮选择 <b>【拍照】</b>（自动唤起手机原生后置超清相机）'
    ' 或 <b>【从相册选择书页】</b></p>',
    unsafe_allow_html=True,
)

upload_file = st.file_uploader(
    "📤 点击此处 — 拍照或选择书页照片",
    type=["jpg", "jpeg", "png", "heic", "webp"],
    key=f"upload_{st.session_state.upload_key}",
    help="支持 JPG / PNG / HEIC / WebP 格式。手机端将唤起原生相机，画质远超网页摄像头。",
    label_visibility="visible",
)

# ============================================================
# 🧠 图像处理管线 — 纯中文 OCR → 直连 Pollinations
# ============================================================
if upload_file is not None:
    # 读取图像字节
    img_bytes = upload_file.read()
    new_hash = hashlib.md5(img_bytes).hexdigest()

    # 仅在新图像时处理
    if new_hash != st.session_state.img_hash:
        st.session_state.img_hash = new_hash
        st.session_state.img_bytes = img_bytes
        st.session_state.show_results = False

        img = Image.open(io.BytesIO(img_bytes))
        st.session_state.img_width = img.width
        st.session_state.img_height = img.height

        # 书页快照预览（折叠）
        with st.expander("👁️ 查看书页快照", expanded=False):
            st.image(img, use_container_width=True)
            st.caption(f"分辨率：{img.width} × {img.height} px")

        # 主处理管线
        with st.status("🧠 视觉大脑正在解析书页...", expanded=True) as status:

            # ================================================
            # 阶段 1：Gemini 纯 OCR — 只识别中文，不生成 prompt
            # ================================================
            st.write("🔍 **阶段 1/2：精准识别书页中文文字...**")

            ocr_prompt = """你的唯一任务是精准识别并提取这张图片中所有可见的中文文字。

规则：
1. 保留原文的段落结构、换行和标点符号。
2. 如果图片中没有中文文字，返回空字符串。
3. 不要添加任何解释、点评或额外内容。
4. 不要翻译，不要总结，只做纯 OCR 提取。

返回一个 JSON，包含一个键 "chinese_text"，值为你识别到的全部中文文字。"""

            json_schema = {
                "type": "OBJECT",
                "properties": {
                    "chinese_text": {"type": "STRING"}
                },
                "required": ["chinese_text"]
            }

            chinese_text = ""

            try:
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[img, ocr_prompt],
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        top_p=0.95,
                        max_output_tokens=2048,
                        response_mime_type="application/json",
                        response_schema=json_schema
                    ),
                )

                raw_response = response.text.strip()
                result = json.loads(raw_response)
                chinese_text = result.get("chinese_text", "").strip()

            except Exception:
                chinese_text = "OCR 识别失败，请重试或更换更清晰的书页照片。"

            st.session_state.ocr_text = chinese_text

            # ================================================
            # 阶段 2：中文直连 Pollinations — 零中间商
            # ================================================
            if chinese_text:
                status.update(
                    label="🎨 阶段 2/2：正在将文字渲染为视觉画作...",
                    state="running",
                )

                # 中文原文 + 固定画质后缀，直接 URL 编码喂给 Pollinations
                final_prompt = chinese_text + STYLE_SUFFIX
                encoded_prompt = urllib.parse.quote(final_prompt, safe="")
                seed_num = random.randint(1, 99999)
                st.session_state.final_image_url = (
                    f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                    f"?width=1024&height=1536&nologo=true&seed={seed_num}"
                )

                status.update(
                    label="🎉 渲染完成！", state="complete", expanded=False
                )
            else:
                status.update(label="⚠️ 未能提取有效文字", state="error")

            st.session_state.show_results = True

        # 处理完成后重跑以渲染结果
        st.rerun()

    # ============================================================
    # 🖼️ 展示结果
    # ============================================================
    if st.session_state.show_results:

        # 重置按钮
        def reset_all():
            st.session_state.upload_key += 1
            st.session_state.img_hash = ""
            st.session_state.img_bytes = None
            st.session_state.ocr_text = ""
            st.session_state.final_image_url = ""
            st.session_state.show_results = False

        st.button(
            "🔄 拍摄新书页",
            on_click=reset_all,
            use_container_width=True,
            type="secondary",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # 书页快照
        with st.expander("👁️ 查看书页快照", expanded=False):
            img = Image.open(io.BytesIO(st.session_state.img_bytes))
            st.image(img, use_container_width=True)
            st.caption(
                f"分辨率：{st.session_state.img_width} × {st.session_state.img_height} px"
            )

        # ① OCR 中文文本
        st.markdown("### 📝 识别的书页文字")
        if st.session_state.ocr_text:
            st.markdown(
                '<div class="result-card"><span class="chip ocr">✦ OCR 识别结果</span>',
                unsafe_allow_html=True,
            )
            st.text_area(
                "书页原文",
                value=st.session_state.ocr_text,
                height=200,
                key="ocr_display",
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("🤔 未在图像中检测到中文字符。请确保书页文字清晰，重新拍摄。")

        # ② AI 画作 — 全宽震撼展示
        if st.session_state.final_image_url:
            st.markdown("### 🖼️ AI 视觉渲染")
            st.markdown(
                '<div style="text-align:center;margin:0.4rem 0 0.6rem;">'
                '<span class="chip art">✦ 画面由你的文字直接驱动 ✦</span></div>',
                unsafe_allow_html=True,
            )
            st.image(
                st.session_state.final_image_url,
                caption="书页文字的视觉具象化",
                use_container_width=True,
            )

            # 直链
            with st.expander("🔗 渲染直链", expanded=False):
                st.code(st.session_state.final_image_url, language="text")

        # 错误回退
        if not st.session_state.ocr_text and not st.session_state.final_image_url:
            st.error(
                "VisionReader 未能从图像中提取有效文字。请尝试：\n\n"
                "1. 确保书页光照充足、文字清晰\n"
                "2. 将手机对准书页正上方拍摄\n"
                "3. 选择高分辨率图片上传"
            )

# ============================================================
# 🏠 空状态引导
# ============================================================
else:
    st.markdown(
        """
    <div style="text-align:center;padding:3rem 1.5rem;
                background:rgba(20,20,40,0.35);border-radius:16px;
                border:1px solid rgba(255,255,255,0.05);margin-top:0.5rem;">
        <div style="font-size:3rem;margin-bottom:0.8rem;opacity:0.3;">📖</div>
        <div style="color:rgba(255,255,255,0.5);font-size:0.95rem;font-weight:600;margin-bottom:0.6rem;">
            开始你的沉浸式阅读之旅
        </div>
        <div style="color:rgba(255,255,255,0.2);font-size:0.78rem;line-height:2.2;">
            点击上方 📤 <b>上传按钮</b> 拍照或选择书页照片<br>
            AI 将自动识别书中文字<br>
            并直接根据原文为你生成视觉画作
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ============================================================
# 📱 底部
# ============================================================
st.markdown(
    """
<div class="footer">
    VisionReader AI v4.0 · 随身视界阅读器<br>
    Powered by Gemini Vision & Pollinations AI
</div>
""",
    unsafe_allow_html=True,
)
