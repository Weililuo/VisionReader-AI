"""
============================================================
VisionReader AI · 随身视界阅读器
移动端 AI 书页渲染器 — 拍照、OCR 识别、意境生图
============================================================
v2.1 稳定版：原生组件数据流 + 极简暗色 UI + 后置摄像头引导
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
                    label="🎨 阶段 2/2：正在将意境渲染至手机画布...",
                    state="running",
                )

                encoded_prompt = urllib.parse.quote(image_prompt, safe="")
                seed_num = random.randint(1, 99999)
                st.session_state.final_image_url = (
                    f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                    f"?width=768&height=1024&nologo=true&seed={seed_num}"
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
    VisionReader AI · 随身视界阅读器<br>
    Powered by Gemini Vision & Pollinations AI
</div>
""",
    unsafe_allow_html=True,
)
