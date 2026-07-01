"""
============================================================
VisionReader AI · 随身视界阅读器  v3.0 完全体
移动端 AI 书页渲染器 — 拍照、OCR 识别、意境生图
============================================================
v3.0: 故事灵魂剥离 · 相机巨幕重绘 · 暗夜赛博朋克 UI
原生数据流 (UploadedFile + MD5 缓存) 100% 不动
"""

import streamlit as st
import google.genai as genai
from google.genai import types
import urllib.parse
from PIL import Image
import json
import re
import random
import io
import hashlib

# ============================================================
# 🔐 核心配置
# ============================================================
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = str(st.secrets["GEMINI_API_KEY"]).strip()
else:
    GEMINI_API_KEY = ""

GEMINI_MODEL = "gemini-2.5-flash"

# ============================================================
# 📱 Streamlit 页面配置
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
# 🎨 v3.0 暗夜赛博朋克主题 CSS — 史诗视觉归来
# ============================================================
st.markdown(
    """
<style>
    /* ══════════════════════════════════════════════════════════
       全局暗夜星空基底
       ══════════════════════════════════════════════════════════ */
    .stApp {
        background: linear-gradient(160deg, #020208 0%, #0a0a1a 50%, #050b1a 100%);
        background-attachment: fixed;
    }

    /* ══════════════════════════════════════════════════════════
       主容器：手机最优宽度 + 舒展间距
       ══════════════════════════════════════════════════════════ */
    .main .block-container {
        max-width: 500px !important;
        padding: 1.2rem 1.2rem 3rem !important;
    }

    /* ══════════════════════════════════════════════════════════
       隐藏无关 chrome
       ══════════════════════════════════════════════════════════ */
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    header[data-testid="stHeader"] { background: transparent !important; }

    /* ══════════════════════════════════════════════════════════
       品牌标题：赛博霓虹渐变
       ══════════════════════════════════════════════════════════ */
    h1 {
        font-size: 2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #c084fc, #818cf8, #22d3ee, #34d399);
        background-size: 300% 300%;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-align: center;
        letter-spacing: 0.04em;
        margin-bottom: 0.15rem !important;
        padding-top: 0.6rem !important;
        line-height: 1.35 !important;
        animation: titleShimmer 5s ease-in-out infinite;
        text-shadow: none !important;
    }

    @keyframes titleShimmer {
        0%, 100% { filter: brightness(1) drop-shadow(0 0 6px rgba(129, 140, 248, 0.3)); }
        50%      { filter: brightness(1.15) drop-shadow(0 0 14px rgba(34, 211, 238, 0.5)); }
    }

    /* ══════════════════════════════════════════════════════════
       副标题
       ══════════════════════════════════════════════════════════ */
    .subtitle {
        text-align: center;
        color: #7171a0;
        font-size: 0.8rem;
        margin-bottom: 1.8rem;
        letter-spacing: 0.08em;
    }

    /* ══════════════════════════════════════════════════════════
       赛博科技感卡片容器 — 方式一 / 方式二
       ══════════════════════════════════════════════════════════ */
    .cyber-card {
        background: rgba(15, 15, 35, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(142, 197, 252, 0.15);
        border-radius: 20px;
        padding: 1.4rem 1.2rem;
        margin-bottom: 1.6rem;
        box-shadow:
            0 0 15px rgba(142, 197, 252, 0.08),
            0 0 40px rgba(139, 92, 246, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.02);
        transition: border-color 0.35s, box-shadow 0.35s;
    }
    .cyber-card:hover {
        border-color: rgba(168, 85, 247, 0.35);
        box-shadow:
            0 0 22px rgba(139, 92, 246, 0.15),
            0 0 55px rgba(34, 211, 238, 0.08);
    }

    /* ══════════════════════════════════════════════════════════
       区块标题
       ══════════════════════════════════════════════════════════ */
    .section-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #c4c4e0;
        letter-spacing: 0.05em;
        margin: 0 0 0.7rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(139, 92, 246, 0.3), transparent);
        margin-left: 4px;
    }

    /* ══════════════════════════════════════════════════════════
       📸 后置摄像头强引导 — 霓虹警示框
       ══════════════════════════════════════════════════════════ */
    .camera-warning {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(249, 115, 22, 0.08));
        border: 1.5px solid rgba(239, 68, 68, 0.5);
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 0.9rem;
        text-align: center;
        animation: warningPulse 2.2s ease-in-out infinite;
        box-shadow: 0 0 18px rgba(239, 68, 68, 0.15);
    }
    .camera-warning span {
        color: #fecaca;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        line-height: 1.7;
    }
    .camera-warning .highlight {
        color: #fbbf24;
        font-size: 0.82rem;
        font-weight: 800;
    }

    @keyframes warningPulse {
        0%, 100% { box-shadow: 0 0 18px rgba(239, 68, 68, 0.15); }
        50%      { box-shadow: 0 0 32px rgba(239, 68, 68, 0.28); }
    }

    /* ══════════════════════════════════════════════════════════
       相机组件 — 巨幕级全屏重绘 🎥
       ══════════════════════════════════════════════════════════ */
    div[data-testid="stCameraInput"] {
        width: 100% !important;
        max-width: 100% !important;
        border-radius: 18px !important;
        overflow: hidden !important;
        border: 2px solid rgba(34, 211, 238, 0.45) !important;
        background: #000 !important;
        margin-bottom: 0.5rem !important;
        box-shadow:
            0 0 20px rgba(34, 211, 238, 0.2),
            0 0 50px rgba(6, 182, 212, 0.08),
            inset 0 0 60px rgba(0, 0, 0, 0.3) !important;
        position: relative !important;
        animation: camGlow 3s ease-in-out infinite;
    }

    @keyframes camGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(34, 211, 238, 0.2), 0 0 50px rgba(6, 182, 212, 0.08); }
        50%      { box-shadow: 0 0 30px rgba(34, 211, 238, 0.35), 0 0 65px rgba(6, 182, 212, 0.15); }
    }

    /* ── 扫描线特效叠加层 ── */
    div[data-testid="stCameraInput"]::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(34, 211, 238, 0.015) 2px,
            rgba(34, 211, 238, 0.015) 4px
        );
        pointer-events: none;
        z-index: 10;
        border-radius: 18px;
    }

    /* ── video 全宽 ── */
    div[data-testid="stCameraInput"] video {
        width: 100% !important;
        max-width: 100% !important;
        object-fit: cover !important;
        border-radius: 16px !important;
    }

    /* ── canvas 全宽 ── */
    div[data-testid="stCameraInput"] canvas {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* ── 相机内部按钮美化 ── */
    div[data-testid="stCameraInput"] button {
        border-radius: 30px !important;
        border: 1px solid rgba(34, 211, 238, 0.4) !important;
        background: rgba(0, 0, 0, 0.6) !important;
        color: #22d3ee !important;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }

    /* ══════════════════════════════════════════════════════════
       文件上传器 — 赛博卡片
       ══════════════════════════════════════════════════════════ */
    [data-testid="stFileUploadDropzone"] {
        border-radius: 18px !important;
        border: 1.5px dashed rgba(139, 92, 246, 0.22) !important;
        padding: 2rem 1.2rem !important;
        background: rgba(139, 92, 246, 0.03) !important;
        transition: border-color 0.3s, background 0.3s, box-shadow 0.3s !important;
        box-shadow: 0 0 12px rgba(139, 92, 246, 0.05) !important;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: rgba(168, 85, 247, 0.5) !important;
        background: rgba(139, 92, 246, 0.06) !important;
        box-shadow: 0 0 25px rgba(139, 92, 246, 0.12) !important;
    }

    /* ══════════════════════════════════════════════════════════
       分割线
       ══════════════════════════════════════════════════════════ */
    .divider-text {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 1.6rem 0;
        color: rgba(255, 255, 255, 0.18);
        font-size: 0.7rem;
        letter-spacing: 0.1em;
    }
    .divider-text::before,
    .divider-text::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.25), transparent);
    }

    /* ══════════════════════════════════════════════════════════
       结果卡片
       ══════════════════════════════════════════════════════════ */
    .result-card {
        background: rgba(20, 20, 40, 0.5);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(142, 197, 252, 0.1);
        border-radius: 18px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
    }

    /* ══════════════════════════════════════════════════════════
       胶囊标签
       ══════════════════════════════════════════════════════════ */
    .chip {
        display: inline-block;
        padding: 0.28rem 0.85rem;
        border-radius: 50px;
        font-size: 0.68rem;
        letter-spacing: 0.06em;
        margin-bottom: 0.6rem;
        font-weight: 600;
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
    }
    .chip.ocr   { background: rgba(96,165,250,0.12);  border:1px solid rgba(96,165,250,0.25);  color:#93c5fd; }
    .chip.prompt{ background: rgba(251,191,36,0.1);   border:1px solid rgba(251,191,36,0.25);  color:#fbbf24; }
    .chip.art   { background: rgba(52,211,153,0.1);   border:1px solid rgba(52,211,153,0.22);  color:#34d399; }

    /* ══════════════════════════════════════════════════════════
       OCR 文本框
       ══════════════════════════════════════════════════════════ */
    .ocr-area textarea {
        background: rgba(15, 15, 30, 0.6) !important;
        border: 1px solid rgba(96, 165, 250, 0.2) !important;
        border-radius: 16px !important;
        color: #d8d8f0 !important;
        font-size: 0.92rem !important;
        line-height: 1.9 !important;
        padding: 0.9rem !important;
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
    }
    .ocr-area textarea:focus {
        border-color: rgba(96, 165, 250, 0.4) !important;
        box-shadow: 0 0 15px rgba(96, 165, 250, 0.1) !important;
    }

    /* ══════════════════════════════════════════════════════════
       代码块 / Prompt 展示
       ══════════════════════════════════════════════════════════ */
    .stCodeBlock {
        border-radius: 16px !important;
        border: 1px solid rgba(251, 191, 36, 0.18) !important;
        background: rgba(10, 10, 25, 0.7) !important;
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        box-shadow: 0 0 12px rgba(251, 191, 36, 0.04);
    }
    .stCodeBlock code {
        font-size: 0.8rem !important;
        line-height: 1.6 !important;
        color: #fcd34d !important;
    }

    /* ══════════════════════════════════════════════════════════
       生成图片
       ══════════════════════════════════════════════════════════ */
    .stImage img {
        border-radius: 18px !important;
        box-shadow:
            0 16px 50px rgba(0, 0, 0, 0.55),
            0 0 30px rgba(139, 92, 246, 0.08) !important;
    }

    /* ══════════════════════════════════════════════════════════
       按钮全局
       ══════════════════════════════════════════════════════════ */
    .stButton > button {
        border-radius: 30px !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        transition: all 0.25s !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    .stButton > button:hover {
        border-color: rgba(139, 92, 246, 0.4) !important;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.15) !important;
    }

    /* ══════════════════════════════════════════════════════════
       展开面板
       ══════════════════════════════════════════════════════════ */
    .streamlit-expanderHeader {
        border-radius: 16px !important;
        background: rgba(20, 20, 40, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        font-size: 0.84rem !important;
        padding: 0.7rem 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* ══════════════════════════════════════════════════════════
       st.status 状态组件
       ══════════════════════════════════════════════════════════ */
    .stStatus {
        border-radius: 16px !important;
        border: 1px solid rgba(142, 197, 252, 0.1) !important;
        background: rgba(15, 15, 35, 0.5) !important;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }

    /* ══════════════════════════════════════════════════════════
       底部
       ══════════════════════════════════════════════════════════ */
    .footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.12);
        font-size: 0.66rem;
        padding: 2.5rem 0 0.5rem;
        letter-spacing: 0.06em;
        line-height: 2;
    }

    /* ══════════════════════════════════════════════════════════
       移动端触控优化
       ══════════════════════════════════════════════════════════ */
    button, .streamlit-expanderHeader {
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
    }

    /* ══════════════════════════════════════════════════════════
       iframe 无边框
       ══════════════════════════════════════════════════════════ */
    iframe { border: none !important; }

    /* ══════════════════════════════════════════════════════════
       滚动条美化
       ══════════════════════════════════════════════════════════ */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.25);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(139, 92, 246, 0.4); }

    /* ══════════════════════════════════════════════════════════
       移动端专属增强 — 间距拉大防重叠
       ══════════════════════════════════════════════════════════ */
    @media (max-width: 640px) {
        .main .block-container {
            padding: 0.8rem 1rem 3rem !important;
        }
        h1 {
            font-size: 1.6rem !important;
        }
        .cyber-card {
            padding: 1.2rem 0.9rem;
            margin-bottom: 1.8rem;
        }
        .result-card {
            padding: 1rem 0.8rem;
            margin: 1rem 0;
        }
        div[data-testid="stCameraInput"] {
            border-radius: 16px !important;
            margin-bottom: 0.8rem !important;
        }
        .section-label {
            margin-bottom: 0.9rem;
        }
    }
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
        console.log('[VisionReader v3.0] getUserMedia patch active → rear camera preferred');
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
# 📸 核心交互区
# ============================================================

# ── 方式一：拍照（赛博卡片容器）──
st.markdown(
    """
<div class="cyber-card">
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="section-label">📸 方式一 · 拍摄书页</p>',
    unsafe_allow_html=True,
)

# ── 🔴 后置摄像头强引导 ──
st.markdown(
    """
<div class="camera-warning">
    <span>
        📸 <span class="highlight">答辩路演提示：</span><br>
        请务必点击相机右上角的 <span class="highlight">🔄 翻转按钮</span><br>
        一键切换至<span class="highlight">后置高清主摄</span>对准书页！
    </span>
</div>
""",
    unsafe_allow_html=True,
)

camera_file = st.camera_input(
    "将后置摄像头对准书页，点击下方「拍照」按钮",
    key=f"cam_{st.session_state.cam_key}",
    help="手机端会自动尝试唤起后置摄像头。若默认为前置，请点击相机界面上的切换按钮。",
)

st.markdown("</div>", unsafe_allow_html=True)

# ── 分割线 ──
st.markdown(
    '<div class="divider-text">✦ 或者 ✦</div>',
    unsafe_allow_html=True,
)

# ── 方式二：上传（赛博卡片容器）──
st.markdown(
    """
<div class="cyber-card">
""",
    unsafe_allow_html=True,
)

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

st.markdown("</div>", unsafe_allow_html=True)

# ── 统一图像源 ──
image_source = camera_file or upload_file

# ============================================================
# 🧠 图像处理管线（原生数据流 100% 不动）
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
            # 阶段 1：Gemini 多模态识别 —— v3.0 故事灵魂剥离
            # ================================================
            st.write("🔍 **阶段 1/2：识别书页文字 & 提炼视觉剧本...**")

            multi_task_prompt = """你现在是好莱坞顶级概念美术总监，曾为《沙丘》《攻壳机动队》《阿基拉》等神作操刀世界观视觉开发。

⚠️ 核心铁律（违者删号重练）：
1. 你面对的是"一张拍下了书页内容的照片"，但你必须**彻底无视"它是一张纸/一本书"这个物理外壳**。你的眼里只能有 `chinese_text` 里的故事情节、世界观、角色和情感。
2. 你创作 `image_prompt` 时，**绝对禁止**在英文 Prompt 中出现以下任何单词：book, paper, page, text, document, print, font, letter, typography, reading, literature, novel, manuscript, scroll。这是死命令——你要画的是**故事本身的画面**，不是画一本书！
3. 你的 `image_prompt` 必须全盘描绘文字里描述的角色外貌、场景氛围、光影情绪、史诗构图。如果原文是魔幻冒险，就画龙与魔法师在熔岩堡对决；如果是科幻机甲，就画赛博格战士在霓虹雨夜中待命；如果是冷冽都市文学，就画孤寂便利店的白炽灯光。
4. 风格基准：Epic fantasy conceptual art, cinematic lighting, hyper-detailed, masterpiece, dark atmosphere, 8K, octane render, trending on ArtStation。
5. 字数：60-180 个英文单词，画面描述越具体越好。

期待你返回的 JSON 必须严格拥有这两个键：
1. "chinese_text": 识别并提取出图片中所有的可见中文内容，保留原文换行与标点。若没有文字，则为空字符串。
2. "image_prompt": 基于书页文字传达的情绪与氛围，创作一句纯英文电影级概念艺术生图提示词。"""

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
                    else "Epic fantasy conceptual art, cinematic lighting, hyper-detailed, masterpiece, dark atmosphere, 8K, dramatic composition, moody and immersive scene"
                )

            st.session_state.ocr_text = chinese_text
            st.session_state.image_prompt = image_prompt

            # ================================================
            # 阶段 2：Pollinations AI 渲染
            # ================================================
            if image_prompt:
                status.update(
                    label="🎨 阶段 2/2：正在将意境渲染至手机画布...",
                    state="running",
                )

                encoded_prompt = urllib.parse.quote(image_prompt, safe="")
                seed_num = random.randint(1, 99999)
                st.session_state.final_image_url = (
                    f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                    f"?width=1024&height=1536&nologo=true&seed={seed_num}"
                )

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
                '<div style="text-align:center;margin:0.5rem 0 0.8rem;">'
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
                <div style="color:rgba(255,255,255,0.3);font-size:0.68rem;margin-bottom:0.2rem;">🔗 渲染直链</div>
                <a href="{st.session_state.final_image_url}" target="_blank"
                   style="font-size:0.62rem;word-break:break-all;opacity:0.45;">
                   {st.session_state.final_image_url}
                </a>
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
# 🏠 空状态引导
# ============================================================
else:
    st.markdown(
        """
    <div class="result-card" style="text-align:center;padding:2.5rem 1.5rem;">
        <div style="font-size:3rem;margin-bottom:0.8rem;opacity:0.35;">📖</div>
        <div style="color:rgba(255,255,255,0.55);font-size:0.95rem;font-weight:700;margin-bottom:0.6rem;">
            开始你的沉浸式阅读之旅
        </div>
        <div style="color:rgba(255,255,255,0.22);font-size:0.78rem;line-height:2.2;">
            点击上方 📸 <b>拍照</b> 或 📤 <b>上传照片</b><br>
            AI 将自动识别书中文字<br>
            为你生成独一无二的电影级视觉画作
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
    VisionReader AI v3.0 · 随身视界阅读器<br>
    Powered by Gemini Vision & Pollinations AI
</div>
""",
    unsafe_allow_html=True,
)
