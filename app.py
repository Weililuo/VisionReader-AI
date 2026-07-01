"""
============================================================
VisionReader AI · 随身视界阅读器
移动端 AI 书页渲染器 — 拍照、OCR 识别、意境生图
============================================================
<<<<<<< HEAD
v2.1 稳定版：原生组件数据流 + 极简暗色 UI + 后置摄像头引导
=======
重构 v2.0：后置摄像头强制唤起 + 霓虹科幻风实体大按键 UI
>>>>>>> 9497f7e71281149dea9571ee85c004b1daa6caae
"""

import streamlit as st
import streamlit.components.v1 as components
import google.genai as genai
from google.genai import types
import urllib.parse
from PIL import Image
import json
import re
import random
<<<<<<< HEAD
import io
import hashlib

# ============================================================
# 🔐 核心配置
# ============================================================
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = str(st.secrets["GEMINI_API_KEY"]).strip()
=======
import base64
import io

# ============================================================
# 🔐 核心配置 — 安全读取云端保险箱
# ============================================================
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = str(st.secrets["GEMINI_API_KEY"])
>>>>>>> 9497f7e71281149dea9571ee85c004b1daa6caae
else:
    GEMINI_API_KEY = ""

GEMINI_MODEL = "gemini-2.5-flash"
<<<<<<< HEAD

# ============================================================
# 📱 Streamlit 页面配置
=======
client = genai.Client(api_key=GEMINI_API_KEY)

# ============================================================
# 📱 Streamlit 页面配置（必须在最前面调用）
>>>>>>> 9497f7e71281149dea9571ee85c004b1daa6caae
# ============================================================
st.set_page_config(
    page_title="VisionReader AI · 视界阅读",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "VisionReader AI — 拍下书页，看见故事",
    },
)

<<<<<<< HEAD
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
if "cam_key" not in st.session_state:
    st.session_state.cam_key = 0
if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0
if "img_hash" not in st.session_state:
    st.session_state.img_hash = ""
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""
if "image_prompt" not in st.session_state:
    st.session_state.image_prompt = ""
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
# 🎨 极简暗色主题 CSS — 轻量、清晰、移动端友好
# ============================================================
st.markdown(
    """
<style>
    /* ── 全局暗色基底 ── */
    .stApp {
        background: linear-gradient(170deg, #080812 0%, #0e0e1e 40%, #0c1420 100%);
        background-attachment: fixed;
    }

    /* ── 主容器：手机最优宽度 + 充足内边距 ── */
    .main .block-container {
        max-width: 480px !important;
        padding: 1rem 1rem 2rem !important;
    }

    /* ── 隐藏无关 chrome ── */
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    header[data-testid="stHeader"] { background: transparent !important; }

    /* ── 标题：简洁渐变 ── */
    h1 {
        font-size: 1.8rem !important;
        font-weight: 750 !important;
        background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-align: center;
        letter-spacing: 0.03em;
        margin-bottom: 0.2rem !important;
        padding-top: 0.3rem !important;
        line-height: 1.4 !important;
    }

    /* ── 副标题 ── */
    .subtitle {
        text-align: center;
        color: #6b6b8a;
        font-size: 0.78rem;
        margin-bottom: 1.2rem;
        letter-spacing: 0.06em;
    }

    /* ── 提示横幅 ── */
    .tip-banner {
        text-align: center;
        padding: 10px 14px;
        margin-bottom: 1.2rem;
        border-radius: 12px;
        background: rgba(96, 165, 250, 0.06);
        border: 1px solid rgba(96, 165, 250, 0.12);
        color: #93c5fd;
        font-size: 0.76rem;
        line-height: 1.6;
    }

    /* ── 区块标题 ── */
    .section-label {
        font-size: 0.85rem;
        font-weight: 650;
        color: #b0b0cc;
        letter-spacing: 0.04em;
        margin: 0.8rem 0 0.5rem;
    }

    /* ── 相机组件：加大圆角 + 浅边框 ── */
    [data-testid="stCameraInput"] {
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        margin-bottom: 0.6rem !important;
    }

    /* ── 文件上传器：卡片式 ── */
    [data-testid="stFileUploadDropzone"] {
        border-radius: 16px !important;
        border: 1px dashed rgba(255,255,255,0.12) !important;
        padding: 1.5rem 1rem !important;
        background: rgba(255,255,255,0.015) !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: rgba(167, 139, 250, 0.35) !important;
    }

    /* ── 分割线 ── */
    .divider-text {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 1rem 0;
        color: rgba(255,255,255,0.18);
        font-size: 0.7rem;
        letter-spacing: 0.08em;
    }
    .divider-text::before,
    .divider-text::after {
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(255,255,255,0.06);
    }

    /* ── 结果卡片 ── */
    .result-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 1rem;
        margin: 0.6rem 0;
    }

    /* ── 胶囊标签 ── */
    .chip {
        display: inline-block;
        padding: 0.22rem 0.7rem;
        border-radius: 50px;
        font-size: 0.66rem;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        font-weight: 550;
    }
    .chip.ocr  { background: rgba(96,165,250,0.1);  border:1px solid rgba(96,165,250,0.2);  color:#93c5fd; }
    .chip.prompt { background: rgba(251,191,36,0.08); border:1px solid rgba(251,191,36,0.2); color:#fbbf24; }
    .chip.art  { background: rgba(52,211,153,0.08); border:1px solid rgba(52,211,153,0.18); color:#34d399; }

    /* ── OCR 文本框 ── */
    .ocr-area textarea {
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(96,165,250,0.15) !important;
        border-radius: 14px !important;
        color: #d0d0e8 !important;
        font-size: 0.9rem !important;
        line-height: 1.85 !important;
        padding: 0.8rem !important;
    }

    /* ── 代码块 ── */
    .stCodeBlock {
        border-radius: 14px !important;
        border: 1px solid rgba(251,191,36,0.14) !important;
        background: rgba(0,0,0,0.2) !important;
    }
    .stCodeBlock code {
        font-size: 0.8rem !important;
        line-height: 1.55 !important;
        color: #fbbf24 !important;
    }

    /* ── 图片 ── */
    .stImage img {
        border-radius: 16px !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.45) !important;
    }

    /* ── 按钮 ── */
    .stButton > button {
        border-radius: 30px !important;
        font-weight: 650 !important;
        letter-spacing: 0.04em !important;
        transition: all 0.2s !important;
    }

    /* ── 展开面板 ── */
    .streamlit-expanderHeader {
        border-radius: 14px !important;
        background: rgba(255,255,255,0.015) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        font-size: 0.82rem !important;
    }

    /* ── 状态组件 ── */
    .stStatus {
        border-radius: 14px !important;
    }

    /* ── 底部 ── */
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.15);
        font-size: 0.65rem;
        padding: 2rem 0 0.5rem;
        letter-spacing: 0.05em;
        line-height: 1.8;
    }

    /* ── 移动端触控 ── */
    button, .streamlit-expanderHeader {
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
    }

    /* ── iframe 无边框 ── */
    iframe { border: none !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 🧬 JS 注入：拦截 getUserMedia → 优先后置摄像头
# ============================================================
st.markdown(
    """
<script>
(function() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        var _orig = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
        navigator.mediaDevices.getUserMedia = function(constraints) {
            if (constraints && constraints.video) {
                if (typeof constraints.video === 'object') {
                    constraints.video.facingMode = { ideal: 'environment' };
                }
            }
            return _orig(constraints);
        };
        console.log('[VisionReader] getUserMedia patch active');
    }
})();
</script>
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
# 💡 后置摄像头引导提示
# ============================================================
st.markdown(
    """
<div class="tip-banner">
    💡 <b>提示：</b>拍照时若默认开启前置镜头，请点击相机界面上的<b>旋转切换图标</b> 🔄 调至后置主摄，书页拍出来会更清晰哦
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 📸 核心交互区
# ============================================================

# ── 方式一：拍照 ──
st.markdown(
    '<p class="section-label">📸 方式一 · 拍摄书页</p>',
    unsafe_allow_html=True,
)
camera_file = st.camera_input(
    "将后置摄像头对准书页，点击下方「拍照」按钮",
    key=f"cam_{st.session_state.cam_key}",
    help="手机端会自动尝试唤起后置摄像头。若默认为前置，请点击相机界面上的切换按钮。",
)

# ── 分割线 ──
st.markdown(
    '<div class="divider-text">或者</div>',
    unsafe_allow_html=True,
)

# ── 方式二：上传 ──
st.markdown(
    '<p class="section-label">📤 方式二 · 上传照片</p>',
    unsafe_allow_html=True,
)
upload_file = st.file_uploader(
    "从相册中选择书页照片",
    type=["jpg", "jpeg", "png", "heic", "webp"],
    key=f"upload_{st.session_state.upload_key}",
    help="支持 JPG / PNG / HEIC / WebP 格式",
)

# ── 统一图像源 ──
image_source = camera_file or upload_file

# ============================================================
# 🧠 图像处理管线
# ============================================================
if image_source is not None:
    # ── 读取图像字节 ──
    img_bytes = image_source.read()
    new_hash = hashlib.md5(img_bytes).hexdigest()

    # ── 仅在新图像或首次加载时处理 ──
    if new_hash != st.session_state.img_hash:
        st.session_state.img_hash = new_hash
        st.session_state.img_bytes = img_bytes  # 持久化，防止跨 rerun 数据丢失
        st.session_state.show_results = False  # 先隐藏旧结果

        img = Image.open(io.BytesIO(img_bytes))
        st.session_state.img_width = img.width
        st.session_state.img_height = img.height

        # ── 书页快照预览（折叠） ──
        with st.expander("👁️ 查看书页快照", expanded=False):
            st.image(img, use_container_width=True)
            st.caption(f"分辨率：{img.width} × {img.height} px")

        # ── 主处理管线 ──
        with st.status("🧠 视觉大脑正在解析书页意境...", expanded=True) as status:

            # ================================================
            # 阶段 1：Gemini 多模态识别
            # ================================================
=======
# ============================================================
# 🧠 会话状态初始化
# ============================================================
if "captured_image_bytes" not in st.session_state:
    st.session_state.captured_image_bytes = None
if "processing_done" not in st.session_state:
    st.session_state.processing_done = False
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""
if "image_prompt" not in st.session_state:
    st.session_state.image_prompt = ""
if "final_image_url" not in st.session_state:
    st.session_state.final_image_url = ""

# ============================================================
# 🎨 极致暗色科幻风 CSS — 霓虹发光、实体大按键、移动端优化
# ============================================================
st.markdown(
    """
<style>
    /* ===== [1] 全局暗色主题基底 + 粒子星空背景 ===== */
    .stApp {
        background: linear-gradient(165deg, #06060f 0%, #0c0c1d 25%, #0a0f1e 50%, #080818 75%, #050510 100%);
        background-attachment: fixed;
    }

    /* ===== [2] 主容器窄屏约束 — 手机最佳宽度 ===== */
    .main .block-container {
        max-width: 500px !important;
        padding: 0.6rem 0.8rem !important;
    }

    /* ===== [3] 隐藏 Streamlit 默认元素 ===== */
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    header[data-testid="stHeader"] { background: transparent !important; }

    /* ===== [4] 标题：流光渐变文字 ===== */
    h1 {
        font-size: 2.05rem !important;
        font-weight: 850 !important;
        background: linear-gradient(135deg, #c084fc 0%, #60a5fa 35%, #34d399 65%, #fbbf24 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-align: center;
        letter-spacing: 0.04em;
        margin-bottom: 0rem !important;
        padding-top: 0.5rem !important;
        line-height: 1.3 !important;
    }

    /* ===== [5] 副标题 ===== */
    .vision-subtitle {
        text-align: center;
        color: #7c7c9e;
        font-size: 0.8rem;
        margin-bottom: 0.3rem;
        letter-spacing: 0.08em;
        font-weight: 400;
    }

    /* ===== [6] 装饰分割线 ===== */
    .vision-divider {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0.4rem 0 1.2rem;
    }
    .vision-divider-line {
        flex: 1;
        height: 1px;
    }

    /* ===== [7] 双列卡片容器 ===== */
    .action-cards-row {
        display: flex;
        gap: 12px;
        margin: 0 0 1.2rem;
        justify-content: center;
    }
    @media (max-width: 380px) {
        .action-cards-row {
            flex-direction: column;
            gap: 10px;
        }
    }

    /* ===== [8] 霓虹动作卡片（Streamlit 外层的匹配样式） ===== */
    .neon-card-camera, .neon-card-upload {
        flex: 1;
        min-width: 140px;
        max-width: 220px;
        padding: 22px 14px 18px;
        border-radius: 20px;
        text-align: center;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .neon-card-camera {
        background: rgba(0, 210, 255, 0.04);
        border: 2px solid rgba(0, 210, 255, 0.28);
        box-shadow: 0 0 12px rgba(0, 210, 255, 0.08), 0 0 36px rgba(0, 210, 255, 0.04);
        animation: neonPulseCyan 3s ease-in-out infinite;
    }
    .neon-card-upload {
        background: rgba(192, 132, 252, 0.04);
        border: 2px solid rgba(192, 132, 252, 0.28);
        box-shadow: 0 0 12px rgba(192, 132, 252, 0.08), 0 0 36px rgba(192, 132, 252, 0.04);
        animation: neonPulsePurple 3s ease-in-out infinite 0.5s;
    }

    @keyframes neonPulseCyan {
        0%, 100% {
            border-color: rgba(0, 210, 255, 0.28);
            box-shadow: 0 0 12px rgba(0, 210, 255, 0.08), 0 0 36px rgba(0, 210, 255, 0.04);
        }
        50% {
            border-color: rgba(0, 210, 255, 0.55);
            box-shadow: 0 0 22px rgba(0, 210, 255, 0.2), 0 0 55px rgba(0, 210, 255, 0.08);
        }
    }
    @keyframes neonPulsePurple {
        0%, 100% {
            border-color: rgba(192, 132, 252, 0.28);
            box-shadow: 0 0 12px rgba(192, 132, 252, 0.08), 0 0 36px rgba(192, 132, 252, 0.04);
        }
        50% {
            border-color: rgba(192, 132, 252, 0.55);
            box-shadow: 0 0 22px rgba(192, 132, 252, 0.2), 0 0 55px rgba(192, 132, 252, 0.08);
        }
    }

    .neon-card-icon {
        font-size: 2.8rem;
        margin-bottom: 6px;
        line-height: 1;
        filter: drop-shadow(0 0 8px currentColor);
    }
    .neon-card-label {
        font-size: 1.05rem;
        font-weight: 750;
        letter-spacing: 0.06em;
        margin-bottom: 4px;
    }
    .neon-card-camera .neon-card-label { color: #bae6fd; }
    .neon-card-upload .neon-card-label { color: #e9d5ff; }

    .neon-card-hint {
        font-size: 0.68rem;
        opacity: 0.55;
        letter-spacing: 0.04em;
    }
    .neon-card-camera .neon-card-hint { color: #7dd3fc; }
    .neon-card-upload .neon-card-hint { color: #c4b5fd; }

    /* ===== [9] 文件上传器覆盖样式 ===== */
    [data-testid="stFileUploader"] section {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    [data-testid="stFileUploadDropzone"] {
        background: rgba(192, 132, 252, 0.04) !important;
        border: 2px solid rgba(192, 132, 252, 0.28) !important;
        border-radius: 20px !important;
        padding: 22px 14px 18px !important;
        text-align: center !important;
        animation: neonPulsePurple 3s ease-in-out infinite 0.5s !important;
        transition: all 0.25s ease !important;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: rgba(192, 132, 252, 0.6) !important;
        box-shadow: 0 0 28px rgba(192, 132, 252, 0.18) !important;
    }
    [data-testid="stFileUploadDropzone"] p {
        color: #e9d5ff !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stFileUploadDropzone"] span {
        color: #c4b5fd !important;
        font-size: 0.68rem !important;
    }
    [data-testid="stFileUploadDropzone"] button {
        background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
        border: none !important;
        border-radius: 30px !important;
        color: #fff !important;
        font-weight: 700 !important;
        padding: 0.5rem 1.5rem !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.04em !important;
        box-shadow: 0 4px 18px rgba(124, 58, 237, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploadDropzone"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 24px rgba(124, 58, 237, 0.5) !important;
    }

    /* ===== [10] 毛玻璃结果卡片 ===== */
    .vision-card {
        background: rgba(255, 255, 255, 0.025);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 18px;
        padding: 1rem 1rem 0.5rem 1rem;
        margin: 0.8rem 0;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }

    /* ===== [11] OCR 文字展示区域 ===== */
    .ocr-text-area textarea {
        background: rgba(255, 255, 255, 0.025) !important;
        border: 1px solid rgba(96, 165, 250, 0.18) !important;
        border-radius: 16px !important;
        color: #d8d8f0 !important;
        font-size: 0.95rem !important;
        line-height: 1.9 !important;
        padding: 0.9rem !important;
        font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif !important;
    }

    /* ===== [12] 代码块（Image Prompt） ===== */
    .stCodeBlock {
        border-radius: 16px !important;
        border: 1px solid rgba(251, 191, 36, 0.16) !important;
        background: rgba(0, 0, 0, 0.25) !important;
    }
    .stCodeBlock code {
        font-size: 0.82rem !important;
        line-height: 1.6 !important;
        color: #fbbf24 !important;
    }

    /* ===== [13] 图片圆角 + 电影级阴影 ===== */
    .stImage img {
        border-radius: 18px !important;
        box-shadow:
            0 20px 60px rgba(0, 0, 0, 0.55),
            0 0 80px rgba(100, 140, 255, 0.1),
            0 0 4px rgba(255, 255, 255, 0.06) !important;
    }

    /* ===== [14] 水平分割线 ===== */
    hr {
        border-color: rgba(255, 255, 255, 0.05) !important;
        margin: 1.2rem 0 !important;
    }

    /* ===== [15] Expander 展开面板 ===== */
    .streamlit-expanderHeader {
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        font-size: 0.88rem !important;
        color: #aaa !important;
    }

    /* ===== [16] 状态组件 ===== */
    .stStatus {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        background: rgba(255, 255, 255, 0.015) !important;
    }

    /* ===== [17] 胶囊标签 ===== */
    .vision-chip {
        display: inline-block;
        padding: 0.28rem 0.85rem;
        border-radius: 50px;
        font-size: 0.7rem;
        letter-spacing: 0.07em;
        margin-bottom: 0.6rem;
        font-weight: 550;
    }
    .vision-chip.ocr {
        background: rgba(96, 165, 250, 0.1);
        border: 1px solid rgba(96, 165, 250, 0.25);
        color: #93c5fd;
    }
    .vision-chip.prompt {
        background: rgba(251, 191, 36, 0.08);
        border: 1px solid rgba(251, 191, 36, 0.25);
        color: #fbbf24;
    }
    .vision-chip.art {
        background: rgba(52, 211, 153, 0.08);
        border: 1px solid rgba(52, 211, 153, 0.22);
        color: #34d399;
    }

    /* ===== [18] 链接 ===== */
    a {
        color: #93c5fd !important;
        text-decoration: none !important;
    }

    /* ===== [19] 信息/错误提示框 ===== */
    .stAlert {
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }

    /* ===== [20] 按钮全局美化 ===== */
    .stButton > button {
        border-radius: 30px !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
    }

    /* ===== [21] 移动端触控优化 ===== */
    button, [data-baseweb="tab"], .streamlit-expanderHeader, .neon-card-camera, .neon-card-upload {
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
    }

    /* ===== [22] 重置按钮特殊样式 ===== */
    .reset-btn > button {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: rgba(255, 255, 255, 0.5) !important;
        font-size: 0.75rem !important;
        padding: 0.35rem 1.2rem !important;
    }
    .reset-btn > button:hover {
        border-color: rgba(255, 255, 255, 0.3) !important;
        color: rgba(255, 255, 255, 0.8) !important;
    }

    /* ===== [23] 底部信息 ===== */
    .vision-footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.18);
        font-size: 0.68rem;
        padding: 2rem 0 0.8rem;
        letter-spacing: 0.06em;
        line-height: 1.8;
    }

    /* ===== [24] iframe 无边框 ===== */
    iframe {
        border: none !important;
        background: transparent !important;
    }

    /* ===== [25] 后置摄像头提示横幅 ===== */
    .camera-tip-banner {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 10px 16px;
        margin: 0 0 1rem;
        border-radius: 14px;
        background: rgba(0, 210, 255, 0.06);
        border: 1px solid rgba(0, 210, 255, 0.15);
        color: #7dd3fc;
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.04em;
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 🧬 JavaScript 注入：双重保险确保后置摄像头
# 策略 1: 拦截 getUserMedia，强制 facingMode: "environment"
# 策略 2: 监听 DOM，为动态创建的文件输入添加 capture 属性
# ============================================================
st.markdown(
    """
<script>
(function() {
    // ── 策略 1: Monkey-patch getUserMedia ──
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const _orig = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
        navigator.mediaDevices.getUserMedia = function(constraints) {
            if (constraints && constraints.video) {
                if (typeof constraints.video === 'object') {
                    constraints.video.facingMode = { ideal: 'environment' };
                } else if (typeof constraints.video === 'string') {
                    constraints.video = {
                        deviceId: constraints.video,
                        facingMode: { ideal: 'environment' }
                    };
                }
            }
            console.log('📸 VisionReader: getUserMedia hijacked → rear camera forced');
            return _orig(constraints);
        };
        console.log('✅ VisionReader: getUserMedia rear-camera patch active');
    }

    // ── 策略 2: MutationObserver 监听文件输入 ──
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) {
                    // 为所有新创建的 file input 补充 capture 属性
                    const inputs = node.tagName === 'INPUT'
                        ? [node]
                        : node.querySelectorAll ? node.querySelectorAll('input[type="file"]') : [];
                    inputs.forEach(function(inp) {
                        if (inp.type === 'file' && inp.accept && inp.accept.includes('image')) {
                            if (!inp.hasAttribute('capture')) {
                                inp.setAttribute('capture', 'environment');
                                console.log('📸 VisionReader: added capture=environment to file input');
                            }
                        }
                    });
                }
            });
        });
    });
    observer.observe(document.body || document.documentElement, {
        childList: true,
        subtree: true
    });
    console.log('✅ VisionReader: DOM observer active for capture attribute injection');
})();
</script>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 🏠 品牌头部
# ============================================================
st.markdown(
    """
<div style="text-align: center;">
    <h1>📖 VisionReader AI</h1>
    <p class="vision-subtitle">拍下书页&nbsp;&nbsp;·&nbsp;&nbsp;看见故事&nbsp;&nbsp;·&nbsp;&nbsp;沉浸意境</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="vision-divider">
    <div class="vision-divider-line" style="background: linear-gradient(90deg, transparent, rgba(192,132,252,0.2));"></div>
    <span style="color: rgba(255,255,255,0.15); font-size: 0.6rem;">✦</span>
    <div class="vision-divider-line" style="background: linear-gradient(90deg, rgba(0,210,255,0.2), transparent);"></div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# ⚠️ 后置摄像头引导提示横幅（仅在没有图片时显示）
# ============================================================
if st.session_state.captured_image_bytes is None:
    st.markdown(
        """
    <div class="camera-tip-banner">
        <span style="font-size: 1.2rem;">📸</span>
        <span>为确保最佳拍摄效果，请使用<b>后置摄像头</b>对准书页拍摄</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ============================================================
# 📸🎨 核心交互区：双巨型霓虹动作卡片
# 使用自定义 HTML 组件，通过 capture="environment" 强制后置摄像头
# ============================================================

# ── 渲染双卡片的自定义 HTML 组件 ──
# 卡片 A：拍摄（capture="environment" → 后置摄像头）
# 卡片 B：上传（标准文件选择器 → 相册/文件管理器）
action_html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
        width: 100%;
        height: 100%;
        background: transparent;
        font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Segoe UI", Roboto, sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .cards-container {
        display: flex;
        gap: 12px;
        width: 100%;
        max-width: 480px;
        padding: 4px 2px;
        justify-content: center;
    }

    @media (max-width: 380px) {
        .cards-container {
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
    }

    /* ── 霓虹卡片通用样式 ── */
    .action-card {
        flex: 1;
        min-width: 140px;
        max-width: 220px;
        padding: 24px 14px 20px;
        border-radius: 20px;
        text-align: center;
        cursor: pointer;
        -webkit-tap-highlight-color: transparent;
        user-select: none;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    .action-card:active {
        transform: scale(0.95);
    }

    /* ── 拍摄卡片：青色霓虹 ── */
    .card-camera {
        background: rgba(0, 210, 255, 0.05);
        border: 2px solid rgba(0, 210, 255, 0.3);
        box-shadow: 0 0 14px rgba(0, 210, 255, 0.1), 0 0 40px rgba(0, 210, 255, 0.05);
        animation: glowCyan 3s ease-in-out infinite;
    }
    .card-camera:active {
        background: rgba(0, 210, 255, 0.12);
        box-shadow: 0 0 24px rgba(0, 210, 255, 0.25), 0 0 60px rgba(0, 210, 255, 0.1);
    }

    /* ── 上传卡片：紫色霓虹 ── */
    .card-upload {
        background: rgba(192, 132, 252, 0.05);
        border: 2px solid rgba(192, 132, 252, 0.3);
        box-shadow: 0 0 14px rgba(192, 132, 252, 0.1), 0 0 40px rgba(192, 132, 252, 0.05);
        animation: glowPurple 3s ease-in-out infinite 0.6s;
    }
    .card-upload:active {
        background: rgba(192, 132, 252, 0.12);
        box-shadow: 0 0 24px rgba(192, 132, 252, 0.25), 0 0 60px rgba(192, 132, 252, 0.1);
    }

    /* ── 霓虹呼吸动画 ── */
    @keyframes glowCyan {
        0%, 100% {
            border-color: rgba(0, 210, 255, 0.3);
            box-shadow: 0 0 14px rgba(0, 210, 255, 0.1), 0 0 40px rgba(0, 210, 255, 0.05);
        }
        50% {
            border-color: rgba(0, 210, 255, 0.6);
            box-shadow: 0 0 24px rgba(0, 210, 255, 0.25), 0 0 60px rgba(0, 210, 255, 0.1);
        }
    }
    @keyframes glowPurple {
        0%, 100% {
            border-color: rgba(192, 132, 252, 0.3);
            box-shadow: 0 0 14px rgba(192, 132, 252, 0.1), 0 0 40px rgba(192, 132, 252, 0.05);
        }
        50% {
            border-color: rgba(192, 132, 252, 0.6);
            box-shadow: 0 0 24px rgba(192, 132, 252, 0.25), 0 0 60px rgba(192, 132, 252, 0.1);
        }
    }

    /* ── 扫描线装饰（拍摄卡片） ── */
    .card-camera::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0, 210, 255, 0.015) 2px,
            rgba(0, 210, 255, 0.015) 4px
        );
        animation: scanLine 8s linear infinite;
        pointer-events: none;
    }
    @keyframes scanLine {
        0% { transform: translateY(0); }
        100% { transform: translateY(50%); }
    }

    /* ── 卡片内容样式 ── */
    .card-icon {
        font-size: 2.8rem;
        line-height: 1;
        margin-bottom: 8px;
        position: relative;
        z-index: 1;
    }
    .card-camera .card-icon {
        filter: drop-shadow(0 0 10px rgba(0, 210, 255, 0.5));
    }
    .card-upload .card-icon {
        filter: drop-shadow(0 0 10px rgba(192, 132, 252, 0.5));
    }

    .card-label {
        font-size: 1.1rem;
        font-weight: 750;
        letter-spacing: 0.07em;
        position: relative;
        z-index: 1;
    }
    .card-camera .card-label { color: #bae6fd; }
    .card-upload .card-label { color: #e9d5ff; }

    .card-hint {
        font-size: 0.7rem;
        opacity: 0.5;
        margin-top: 6px;
        letter-spacing: 0.05em;
        position: relative;
        z-index: 1;
    }
    .card-camera .card-hint { color: #7dd3fc; }
    .card-upload .card-hint { color: #c4b5fd; }

    /* ── 成功勾选标识 ── */
    .card-check {
        display: none;
        position: absolute;
        top: 10px;
        right: 12px;
        font-size: 1.2rem;
        z-index: 2;
    }
    .card-done .card-check { display: block; }
    .card-camera .card-check { color: #22d3ee; }
    .card-upload .card-check { color: #c084fc; }

    /* ── 隐藏文件输入 ── */
    .hidden-input {
        display: none !important;
    }
</style>
</head>
<body>

<div class="cards-container">

    <!-- ═══ 卡片 A：拍摄书页 → 后置摄像头 ═══ -->
    <div class="action-card card-camera" id="cameraCard"
         onclick="document.getElementById('cameraInput').click()">
        <div class="card-check">✓</div>
        <div class="card-icon">📸</div>
        <div class="card-label">拍摄书页</div>
        <div class="card-hint">后置摄像头 · 拍书更清晰</div>
    </div>
    <input type="file" id="cameraInput" class="hidden-input"
           accept="image/*" capture="environment"
           onchange="handleFileSelect(this, 'cameraCard')">

    <!-- ═══ 卡片 B：上传照片 → 相册/文件 ═══ -->
    <div class="action-card card-upload" id="uploadCard"
         onclick="document.getElementById('uploadInput').click()">
        <div class="card-check">✓</div>
        <div class="card-icon">📤</div>
        <div class="card-label">上传照片</div>
        <div class="card-hint">从相册选择 · JPG/PNG/HEIC</div>
    </div>
    <input type="file" id="uploadInput" class="hidden-input"
           accept="image/*,.heic,.heif,.webp"
           onchange="handleFileSelect(this, 'uploadCard')">

</div>

<script>
    /**
     * 处理文件选择 → 读取为 base64 → 通过 postMessage 发送给 Streamlit
     */
    function handleFileSelect(input, cardId) {
        if (!input.files || !input.files[0]) return;

        var file = input.files[0];

        // ── 视觉反馈：短暂显示勾选标识 ──
        var card = document.getElementById(cardId);
        card.classList.add('card-done');
        setTimeout(function() { card.classList.remove('card-done'); }, 1500);

        // ── 读取文件为 base64 Data URL ──
        var reader = new FileReader();
        reader.onload = function(e) {
            // 通过 Streamlit 组件通信协议发送数据
            var payload = {
                dataUrl: e.target.result,
                fileName: file.name,
                fileSize: file.size,
                source: cardId === 'cameraCard' ? 'camera' : 'upload'
            };

            // 使用 Streamlit 标准组件桥接协议
            window.parent.postMessage({
                isStreamlitMessage: true,
                type: 'streamlit:setComponentValue',
                data: payload
            }, '*');
        };
        reader.onerror = function() {
            console.error('❌ VisionReader: 文件读取失败');
        };
        reader.readAsDataURL(file);
    }

    console.log('✅ VisionReader: 双卡片动作面板已就绪');
    console.log('📸 拍摄卡片 → capture=environment (后置摄像头)');
    console.log('📤 上传卡片 → 标准文件选择器');
</script>

</body>
</html>
"""

# ── 渲染自定义组件 ──
component_result = components.html(action_html, height=190, scrolling=False)

# ── 解析组件返回的数据 ──
if component_result and isinstance(component_result, dict) and "dataUrl" in component_result:
    try:
        data_url = component_result["dataUrl"]
        # 解析 base64 data URL: "data:image/jpeg;base64,/9j/4AAQ..."
        if "," in data_url:
            header, encoded = data_url.split(",", 1)
            st.session_state.captured_image_bytes = base64.b64decode(encoded)
            st.session_state.processing_done = False  # 重置处理状态
            st.rerun()
    except Exception as e:
        st.error(f"图片解析失败：{e}")

# ============================================================
# 🧠 VisionReader AI 全链路处理管线
# ============================================================
if st.session_state.captured_image_bytes is not None:

    # ── 重置按钮 ──
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🔄 拍摄新书页", key="reset_btn", use_container_width=True):
            # 清空所有会话状态
            st.session_state.captured_image_bytes = None
            st.session_state.processing_done = False
            st.session_state.ocr_text = ""
            st.session_state.image_prompt = ""
            st.session_state.final_image_url = ""
            st.rerun()

    # ── 读取图片 ──
    img = Image.open(io.BytesIO(st.session_state.captured_image_bytes))

    # ── 书页快照预览（折叠） ──
    with st.expander("👁️ 查看书页快照", expanded=False):
        st.image(img, use_container_width=True)
        st.caption(f"分辨率：{img.width} × {img.height} px")

    # ── 仅在尚未处理时执行管线 ──
    if not st.session_state.processing_done:

        with st.status(
            "🧠 视觉大脑正在解析书页意境...", expanded=True
        ) as pipeline_status:

            # ========================================================
            # 阶段 1：Gemini 多模态 — OCR 文字提取 + 意境 Prompt 生成
            # ========================================================
>>>>>>> 9497f7e71281149dea9571ee85c004b1daa6caae
            st.write("🔍 **阶段 1/2：识别书页文字 & 提炼视觉剧本...**")

            multi_task_prompt = """你是一个顶级的 OCR 文字识别专家与电影级场景架构师。
请仔细阅读输入图片中的书页内容，并按要求生成 JSON 输出。

期待你返回的 JSON 必须严格拥有这两个键：
1. "chinese_text": 识别并提取出图片中所有的可见中文内容，保留原文换行与标点。若没有文字，则为空字符串。
2. "image_prompt": 基于书页文字传达的情绪与氛围，创作一句长 60-180 词、极具视觉冲击力的纯英文电影级生图提示词。必须包含强烈的光影调性与沉浸构图。"""

            json_schema = {
                "type": "OBJECT",
                "properties": {
                    "chinese_text": {"type": "STRING"},
                    "image_prompt": {"type": "STRING"}
                },
                "required": ["chinese_text", "image_prompt"]
            }

            chinese_text = ""
            image_prompt = ""

            try:
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[img, multi_task_prompt],
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        top_p=0.95,
                        max_output_tokens=2048,
                        response_mime_type="application/json",
                        response_schema=json_schema
                    ),
                )

                raw_response = response.text.strip()
                result = json.loads(raw_response)
                chinese_text = result.get("chinese_text", "").strip()
                image_prompt = result.get("image_prompt", "").strip()

<<<<<<< HEAD
            except Exception as api_err:
                raw_text = (
                    response.text.strip()
                    if 'response' in locals() and response.text
                    else str(api_err)
                )
                cn_blocks = re.findall(r"[一-鿿]+", raw_text)
                chinese_text = "\n".join(cn_blocks) if cn_blocks else "未能完全自动结构化文本"
                en_blocks = re.findall(r"[a-zA-Z\s\,\.\-\'\"]{20,}", raw_text)
                image_prompt = (
                    max(en_blocks, key=len).strip()
                    if en_blocks
                    else "Cinematic book concept art scenery, dramatic lighting"
                )

            st.session_state.ocr_text = chinese_text
            st.session_state.image_prompt = image_prompt

            # ================================================
            # 阶段 2：Pollinations AI 渲染
            # ================================================
            if image_prompt:
                status.update(
=======
                pipeline_status.update(
                    label="✅ 阶段 1/2 完成：文字已提取，意境剧本已生成",
                    state="running",
                )

            except Exception as api_err:
                # 终极保底兜底机制：启发式降级恢复
                raw_text = response.text.strip() if 'response' in locals() and response.text else str(api_err)

                cn_blocks = re.findall(r"[一-鿿]+", raw_text)
                chinese_text = "\n".join(cn_blocks) if cn_blocks else "未能完全自动结构化文本"

                en_blocks = re.findall(r"[a-zA-Z\s\,\.\-\'\"]{20,}", raw_text)
                image_prompt = max(en_blocks, key=len).strip() if en_blocks else "Cinematic book concept art scenery, dramatic lighting"

                pipeline_status.update(
                    label="✅ 阶段 1/2 完成（已安全降级恢复）", state="running"
                )

            # ── 持久化到会话状态 ──
            st.session_state.ocr_text = chinese_text
            st.session_state.image_prompt = image_prompt

            # ========================================================
            # 阶段 2：Pollinations AI 渲染图像
            # ========================================================
            if image_prompt:
                pipeline_status.update(
>>>>>>> 9497f7e71281149dea9571ee85c004b1daa6caae
                    label="🎨 阶段 2/2：正在将意境渲染至手机画布...",
                    state="running",
                )

                encoded_prompt = urllib.parse.quote(image_prompt, safe="")
                seed_num = random.randint(1, 99999)
<<<<<<< HEAD
                st.session_state.final_image_url = (
=======
                final_image_url = (
>>>>>>> 9497f7e71281149dea9571ee85c004b1daa6caae
                    f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                    f"?width=768&height=1024&nologo=true&seed={seed_num}"
                )

<<<<<<< HEAD
                status.update(
                    label="🎉 沉浸式视界已同步！", state="complete", expanded=False
                )
            elif not chinese_text:
                status.update(label="⚠️ 未能提取有效内容", state="error")

            st.session_state.show_results = True

        # 处理完成后重跑一次以渲染结果
        st.rerun()

    # ============================================================
    # 🖼️ 展示结果（管线已完成）
    # ============================================================
    if st.session_state.show_results:

        # ── 重置按钮 ──
        def reset_all():
            st.session_state.cam_key += 1
            st.session_state.upload_key += 1
            st.session_state.img_hash = ""
            st.session_state.img_bytes = None
            st.session_state.ocr_text = ""
            st.session_state.image_prompt = ""
            st.session_state.final_image_url = ""
            st.session_state.show_results = False

        st.button(
            "🔄 拍摄新书页",
            on_click=reset_all,
            use_container_width=True,
            type="secondary",
        )

        # ── 书页快照 ──
        with st.expander("👁️ 查看书页快照", expanded=False):
            img = Image.open(io.BytesIO(st.session_state.img_bytes))
            st.image(img, use_container_width=True)
            st.caption(
                f"分辨率：{st.session_state.img_width} × {st.session_state.img_height} px"
            )

        # ── ① OCR 中文文本 ──
        st.markdown("### 📝 扫描到的原始文字")
        if st.session_state.ocr_text:
            st.markdown(
                '<div class="result-card"><span class="chip ocr">✦ OCR 识别结果</span>',
                unsafe_allow_html=True,
            )
            st.text_area(
                "书页原文",
                value=st.session_state.ocr_text,
                height=180,
                key="ocr_display",
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("🤔 未在图像中检测到中文字符。请确保书页文字清晰，重新拍摄。")

        # ── ② Image Prompt ──
        if st.session_state.image_prompt:
            st.markdown("### 🎬 提炼的视觉剧本")
            st.markdown(
                '<div class="result-card"><span class="chip prompt">✦ 电影级 Image Prompt</span>',
                unsafe_allow_html=True,
            )
            st.code(st.session_state.image_prompt, language="text")
            st.markdown("</div>", unsafe_allow_html=True)

        # ── ③ AI 画作 ──
        if st.session_state.final_image_url:
            st.markdown("### 🖼️ 沉浸意境剧场")
            st.markdown(
                '<div style="text-align:center;margin:0.3rem 0 0.6rem;">'
                '<span class="chip art">✦ AI 渲染画作 ✦</span></div>',
                unsafe_allow_html=True,
            )
            st.image(
                st.session_state.final_image_url,
                caption="当前书页的视觉具象化展现",
                use_container_width=True,
            )

            # 直链
            st.markdown("---")
            st.markdown(
                f"""
            <div class="result-card" style="text-align:center;">
                <div style="color:rgba(255,255,255,0.35);font-size:0.68rem;margin-bottom:0.2rem;">🔗 渲染直链</div>
                <a href="{st.session_state.final_image_url}" target="_blank"
                   style="font-size:0.62rem;word-break:break-all;opacity:0.5;">
                   {st.session_state.final_image_url}
                </a>
=======
                st.session_state.final_image_url = final_image_url

                pipeline_status.update(
                    label="🎉 沉浸式视界已同步！", state="complete", expanded=False
                )
            elif not chinese_text:
                pipeline_status.update(label="⚠️ 未能提取有效内容", state="error")

            # ── 标记处理完成 ──
            st.session_state.processing_done = True
            st.rerun()

    # ============================================================
    # 🖼️ 展示结果（处理完成后）
    # ============================================================
    else:
        # ── 展示 ①：OCR 提取的中文原始文本 ──
        st.markdown("### 📝 扫描到的原始文字")

        if st.session_state.ocr_text:
            st.markdown(
                """
            <div class="vision-card">
                <span class="vision-chip ocr">✦ OCR 识别结果</span>
            """,
                unsafe_allow_html=True,
            )
            st.text_area(
                "书页原文",
                value=st.session_state.ocr_text,
                height=180,
                key="ocr_display",
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info(
                "🤔 未在图像中检测到中文字符。"
                "请确保拍摄的书页包含清晰的中文文字，并重新拍摄。"
            )

        # ── 展示 ②：Gemini 提炼的英文 Image Prompt ──
        if st.session_state.image_prompt:
            st.markdown("### 🎬 提炼的视觉剧本")
            st.markdown(
                """
            <div class="vision-card">
                <span class="vision-chip prompt">✦ 电影级 Image Prompt</span>
            """,
                unsafe_allow_html=True,
            )
            st.code(st.session_state.image_prompt, language="text")
            st.markdown("</div>", unsafe_allow_html=True)

        # ── 展示 ③：AI 渲染画作 ──
        if st.session_state.final_image_url:
            st.markdown("### 🖼️ 沉浸意境剧场")
            st.markdown(
                """
            <div style="text-align: center; margin: 0.3rem 0 0.6rem;">
                <span class="vision-chip art">✦ AI 渲染画作 ✦</span>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.image(
                st.session_state.final_image_url,
                caption="当前书页的视觉具象化展现",
                use_container_width=True,
            )

            # ── 直链分享 ──
            st.markdown("---")
            st.markdown(
                f"""
            <div class="vision-card" style="text-align: center;">
                <div style="color: rgba(255,255,255,0.4); font-size: 0.7rem; margin-bottom: 0.2rem;">
                    🔗 渲染直链
                </div>
                <a href="{st.session_state.final_image_url}" target="_blank" style="
                    font-size: 0.65rem;
                    word-break: break-all;
                    opacity: 0.55;
                ">{st.session_state.final_image_url}</a>
>>>>>>> 9497f7e71281149dea9571ee85c004b1daa6caae
            </div>
            """,
                unsafe_allow_html=True,
            )

        # ── 错误回退 ──
        if not st.session_state.ocr_text and not st.session_state.image_prompt:
            st.error(
                "VisionReader 未能从图像中提取有效文字或生成视觉提示词。"
                "请尝试：\n"
                "1. 确保书页光照充足、文字清晰\n"
                "2. 将手机对准书页正上方拍摄\n"
                "3. 使用「上传照片」选择高分辨率图片"
            )

# ============================================================
<<<<<<< HEAD
# 🏠 空状态引导
=======
# 🏠 空状态引导 — 优雅的首次访问界面
>>>>>>> 9497f7e71281149dea9571ee85c004b1daa6caae
# ============================================================
else:
    st.markdown(
        """
<<<<<<< HEAD
    <div class="result-card" style="text-align:center;padding:2rem 1.2rem;">
        <div style="font-size:2.8rem;margin-bottom:0.6rem;opacity:0.4;">📖</div>
        <div style="color:rgba(255,255,255,0.6);font-size:0.9rem;font-weight:600;margin-bottom:0.5rem;">
            开始你的沉浸式阅读之旅
        </div>
        <div style="color:rgba(255,255,255,0.28);font-size:0.75rem;line-height:2;">
            点击上方 📸 <b>拍照</b> 或 📤 <b>上传照片</b><br>
            AI 将自动识别书中文字<br>
            为你生成独一无二的电影级视觉画作
        </div>
=======
    <div class="vision-card" style="text-align: center; padding: 2rem 1.2rem;">
        <div style="font-size: 3.2rem; margin-bottom: 0.8rem; opacity: 0.45;">📖</div>
        <div style="
            color: rgba(255,255,255,0.7);
            font-size: 0.95rem;
            font-weight: 650;
            margin-bottom: 0.5rem;
            letter-spacing: 0.04em;
        ">
            开始你的沉浸式阅读之旅
        </div>
        <div style="
            color: rgba(255,255,255,0.32);
            font-size: 0.78rem;
            line-height: 1.9;
        ">
            点击上方 <span style="color: #7dd3fc; font-weight: 550;">📸 拍摄书页</span>
            或 <span style="color: #c4b5fd; font-weight: 550;">📤 上传照片</span><br>
            AI 将自动识别书中文字<br>
            为你生成独一无二的电影级视觉画作
        </div>
        <div style="
            margin-top: 1.2rem;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        ">
            <span style="color: rgba(255,255,255,0.2); font-size: 0.65rem;">📸 拍摄</span>
            <span style="color: rgba(255,255,255,0.1); font-size: 0.55rem;">→</span>
            <span style="color: rgba(255,255,255,0.2); font-size: 0.65rem;">🔍 识别</span>
            <span style="color: rgba(255,255,255,0.1); font-size: 0.55rem;">→</span>
            <span style="color: rgba(255,255,255,0.2); font-size: 0.65rem;">🎨 生图</span>
        </div>
>>>>>>> 9497f7e71281149dea9571ee85c004b1daa6caae
    </div>
    """,
        unsafe_allow_html=True,
    )

# ============================================================
<<<<<<< HEAD
# 📱 底部
# ============================================================
st.markdown(
    """
<div class="footer">
=======
# 📱 底部品牌信息
# ============================================================
st.markdown(
    """
<div class="vision-footer">
>>>>>>> 9497f7e71281149dea9571ee85c004b1daa6caae
    VisionReader AI · 随身视界阅读器<br>
    Powered by Gemini Vision & Pollinations AI
</div>
""",
    unsafe_allow_html=True,
)
