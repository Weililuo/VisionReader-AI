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
STYLE_SUFFIX = (
    ", A comprehensive widescreen ensemble poster, an aventuring party, grouping all"
    " standard characters described into a unified fantasy cinematic scenery,"
    " 8-bit pixel art style, high detailed masterwork"
)

# ============================================================
# 📱 Streamlit 页面配置
# ============================================================
st.set_page_config(
    page_title="🕹️ VisionReader AI · 像素视界",
    page_icon="👾",
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
    /* ================================================
       8-BIT PAC-MAN ARCADE THEME · 吃豆人复古像素风
       ================================================ */

    /* 全局 — 吃豆人经典纯黑底 */
    .stApp {
        background: #000000;
    }

    /* 隐藏无关 chrome */
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    header[data-testid="stHeader"] { background: transparent !important; }

    /* CRT 扫描线叠加（复古街机屏） */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: repeating-linear-gradient(
            0deg,
            rgba(0,0,0,0.12) 0px,
            rgba(0,0,0,0.12) 2px,
            transparent 2px,
            transparent 4px
        );
        pointer-events: none;
        z-index: 9999;
    }

    /* 主容器 */
    .main .block-container {
        max-width: 900px !important;
        padding: 2rem 1.5rem 3rem !important;
    }

    /* 品牌标题 — 吃豆人亮黄 */
    h1 {
        font-family: 'Courier New', monospace !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #ffff00 !important;
        text-align: center;
        letter-spacing: 0.06em;
        margin-bottom: 0.3rem !important;
        padding-top: 1rem !important;
        text-shadow:
            3px 3px 0px #000000,
            0px 0px 20px rgba(255,255,0,0.4);
        image-rendering: pixelated;
    }

    /* 全局正文 — 等宽像素字体 */
    body, p, div, span, label, button, input, textarea, caption, .stMarkdown {
        font-family: 'Courier New', monospace !important;
    }

    /* 副标题 — 幽灵青色 */
    .subtitle {
        text-align: center;
        color: #00ffff;
        font-size: 0.85rem;
        margin-bottom: 2.2rem;
        letter-spacing: 0.08em;
        text-shadow: 0px 0px 10px rgba(0,255,255,0.5);
    }

    /* 上传提示 */
    .upload-hint {
        text-align: center;
        color: #ffff00;
        font-size: 0.92rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        line-height: 1.8;
    }

    /* ================================================
       上传区 — 街机 "INSERT COIN" 像素大色块
       ================================================ */
    [data-testid="stFileUploadDropzone"] {
        border-radius: 0px !important;
        border: 4px solid #0000ff !important;
        padding: 2.8rem 1.5rem !important;
        background: #000000 !important;
        color: #ffff00 !important;
        font-family: 'Courier New', monospace !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        box-shadow:
            inset 0 0 20px rgba(0,0,255,0.2),
            0 0 15px rgba(0,0,255,0.4),
            8px 8px 0px #000080 !important;
        image-rendering: pixelated;
        transition: none !important;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #ffff00 !important;
        box-shadow:
            inset 0 0 30px rgba(0,0,255,0.3),
            0 0 25px rgba(255,255,0,0.5),
            8px 8px 0px #808000 !important;
    }

    /* ================================================
       结果卡片 — 霓虹蓝迷宫围墙
       ================================================ */
    .result-card {
        background: #000000;
        border: 3px solid #0000ff;
        border-radius: 0px;
        padding: 1.2rem;
        margin: 0.6rem 0;
        box-shadow: 0 0 10px rgba(0,0,255,0.3), 4px 4px 0px #000080;
        font-family: 'Courier New', monospace;
    }

    /* OCR 文本框 — 幽灵青色发光 */
    .ocr-area textarea {
        background: #000000 !important;
        border: 3px solid #0000ff !important;
        border-radius: 0px !important;
        color: #00ffff !important;
        font-family: 'Courier New', monospace !important;
        font-size: 0.9rem !important;
        line-height: 1.8 !important;
        padding: 0.8rem !important;
        box-shadow:
            inset 0 0 15px rgba(0,0,255,0.1),
            0 0 10px rgba(0,0,255,0.2);
    }

    /* 生成图片展示 — 像素画框 */
    .stImage img {
        border-radius: 0px !important;
        border: 3px solid #0000ff !important;
        box-shadow:
            0 0 20px rgba(0,0,255,0.4),
            0 12px 40px rgba(0,0,0,0.5),
            4px 4px 0px #000080 !important;
        image-rendering: pixelated;
    }

    /* ================================================
       按钮 — 街机像素大色块 "START GAME"
       ================================================ */
    .stButton > button {
        border-radius: 0px !important;
        font-family: 'Courier New', monospace !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em !important;
        border: 3px solid #0000ff !important;
        background: #000000 !important;
        color: #ffff00 !important;
        box-shadow: 4px 4px 0px #000080 !important;
        text-transform: uppercase;
        transition: none !important;
        image-rendering: pixelated;
        padding: 0.5rem 1.5rem !important;
    }
    .stButton > button:hover {
        border-color: #ffff00 !important;
        color: #ffff00 !important;
        box-shadow:
            4px 4px 0px #808000,
            0 0 15px rgba(255,255,0,0.3) !important;
    }
    .stButton > button:active {
        transform: translate(2px, 2px);
        box-shadow: 2px 2px 0px #000080 !important;
    }

    /* 展开面板 */
    .streamlit-expanderHeader {
        border-radius: 0px !important;
        background: #000000 !important;
        border: 2px solid #0000ff !important;
        font-family: 'Courier New', monospace !important;
        font-size: 0.82rem !important;
        color: #00ffff !important;
    }

    /* 状态组件 */
    .stStatus {
        border-radius: 0px !important;
        border: 3px solid #0000ff !important;
        background: #000000 !important;
        font-family: 'Courier New', monospace !important;
    }

    /* 分割线 — 像素虚线迷宫墙 */
    hr {
        border: none !important;
        border-top: 2px dashed #0000ff !important;
        margin: 1.6rem 0 !important;
    }

    /* 底部 */
    .footer {
        text-align: center;
        color: #0000ff;
        font-family: 'Courier New', monospace;
        font-size: 0.64rem;
        padding: 2.5rem 0 0.5rem;
        letter-spacing: 0.05em;
        text-shadow: 0px 0px 6px rgba(0,0,255,0.4);
    }

    /* 滚动条 — 霓虹蓝像素条 */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #000000; }
    ::-webkit-scrollbar-thumb {
        background: #0000ff;
        border-radius: 0px;
        box-shadow: 0 0 6px rgba(0,0,255,0.5);
    }

    /* 胶囊标签 — 像素幽灵色 */
    .chip {
        display: inline-block;
        padding: 0.25rem 0.8rem;
        border-radius: 0px;
        font-family: 'Courier New', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.06em;
        margin-bottom: 0.6rem;
        font-weight: 700;
    }
    .chip.ocr {
        background: #000000;
        border: 2px solid #00ffff;
        color: #00ffff;
        text-shadow: 0 0 6px rgba(0,255,255,0.5);
    }
    .chip.art {
        background: #000000;
        border: 2px solid #ffb8ff;
        color: #ffb8ff;
        text-shadow: 0 0 6px rgba(255,184,255,0.5);
    }

    /* Streamlit 原生通知条 */
    .stAlert {
        border-radius: 0px !important;
        border: 2px solid #0000ff !important;
        background: #000000 !important;
        font-family: 'Courier New', monospace !important;
    }

    /* 移动端适配 */
    @media (max-width: 640px) {
        .main .block-container {
            padding: 1rem 1rem 3rem !important;
        }
        h1 {
            font-size: 1.4rem !important;
        }
        [data-testid="stFileUploadDropzone"] {
            padding: 2rem 1rem !important;
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
<h1>👾 VisionReader AI</h1>
<p class="subtitle">🕹️ 拍下书页 · 看见故事 · 像素视界</p>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 📤 唯一上传区 — 巨型、直观、原生相机/相册
# ============================================================
st.markdown(
    '<p class="upload-hint">'
    '🕹️ 点击下方 <b>【INSERT COIN】</b> 按钮 — 选择 '
    '<b>【拍照】</b>（自动唤起手机原生后置超清相机）或 <b>【从相册选择】</b></p>',
    unsafe_allow_html=True,
)

upload_file = st.file_uploader(
    "🕹️ INSERT COIN — 点击拍照或选择书页",
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
                seed_num = 42520
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
            "🕹️ 拍摄新书页",
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
                background:#000000;border-radius:0px;
                border:3px solid #0000ff;margin-top:0.5rem;
                box-shadow:0 0 15px rgba(0,0,255,0.3),4px 4px 0px #000080;">
        <div style="font-family:'Courier New',monospace;font-size:3rem;margin-bottom:0.8rem;opacity:0.9;
                    text-shadow:0 0 15px rgba(255,255,0,0.5);">👾</div>
        <div style="font-family:'Courier New',monospace;color:#ffff00;font-size:0.95rem;font-weight:700;margin-bottom:0.6rem;
                    text-shadow:0 0 10px rgba(255,255,0,0.3);">
            ▸ READY TO PLAY ◂
        </div>
        <div style="font-family:'Courier New',monospace;color:#00ffff;font-size:0.78rem;line-height:2.2;
                    text-shadow:0 0 5px rgba(0,255,255,0.3);">
            点击上方 🕹️ <b>INSERT COIN</b> 拍照或选择书页照片<br>
            AI 将自动识别书中文字<br>
            并直接根据原文为你生成像素视觉画作
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
    🕹️ VisionReader AI v5.0 · 像素视界阅读器<br>
    Powered by Gemini Vision & Pollinations AI
</div>
""",
    unsafe_allow_html=True,
)
