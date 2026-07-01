"""
============================================================
VisionReader AI · Premium Pixel Art Book Reader  v6.0  Final
HD Upload → Pure OCR → Direct Pollinations Image Generation
Style: Minimal Black Rectilinear Pixel Art (Production Ready)
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

# ============================================================
# 🔐 Core Configuration
# ============================================================
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = str(st.secrets["GEMINI_API_KEY"]).strip()
else:
    GEMINI_API_KEY = ""

GEMINI_MODEL = "gemini-2.5-flash"

# Pollinations fixed quality suffix (deterministic generation, fixed seed 42520)
STYLE_SUFFIX = (
    ", A comprehensive widescreen ensemble poster, an adventuring party, grouping all"
    " standard characters described into a unified fantasy cinematic scenery,"
    " 8-bit pixel art style, high detailed masterwork"
)

# ============================================================
# 📱 Streamlit Page Configuration
# ============================================================
st.set_page_config(
    page_title="VisionReader AI · Pixel Reader",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "VisionReader AI — Snap a page, see the story unfold.",
    },
)

if not GEMINI_API_KEY:
    st.error(
        "Gemini API Key not configured. Please add `GEMINI_API_KEY` in"
        " `.streamlit/secrets.toml` (local) or Streamlit Cloud Secrets."
    )
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# ============================================================
# 🧠 Session State Initialization
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
# 🎨 Premium Minimal Black Pixel-Art CSS — Clean & Production Ready
# ============================================================
st.markdown(
    """
<style>
    /* ================================================
       Premium Pixel Art · VisionReader Theme
       Pure black · Pixel-blue borders · No scanlines
       ================================================ */

    /* Global pure black background */
    .stApp {
        background: #000000;
    }

    /* Hide irrelevant chrome */
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    header[data-testid="stHeader"] { background: transparent !important; }

    /* Main container — centered with breathing room */
    .main .block-container {
        max-width: 900px !important;
        padding: 2rem 1.5rem 3rem !important;
    }

    /* Brand title — pixel white, understated power */
    h1 {
        font-family: 'Courier New', monospace !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        text-align: center;
        letter-spacing: 0.06em;
        margin-bottom: 0.3rem !important;
        padding-top: 1rem !important;
    }

    /* Global body — monospace pixel font */
    body, p, div, span, label, button, input, textarea, caption, .stMarkdown {
        font-family: 'Courier New', monospace !important;
    }

    /* Subtitle / tagline — pixel blue, one clean line */
    .subtitle {
        text-align: center;
        color: #4a90d9;
        font-size: 0.88rem;
        margin-bottom: 2rem;
        letter-spacing: 0.04em;
    }

    /* ================================================
       Upload Zone — clean rectilinear pixel frame,
       flat grey blocks, no text overlap artifacts
       ================================================ */
    [data-testid="stFileUploadDropzone"] {
        border-radius: 0px !important;
        border: 3px solid #0000ff !important;
        background: #0a0a0a !important;
        padding: 2.5rem 1.5rem !important;
    }

    /* Aggressively fix the "uploadupload" text overlap bug —
       hide Streamlit's built-in button pseudo-text and label
       that conflict with our pixel custom CSS */
    div[data-testid="stFileUploader"] section button::before {
        content: "" !important;
    }
    div[data-testid="stFileUploader"] label {
        display: none !important;
    }

    /* ================================================
       Result Cards — pixel-blue rectilinear border
       ================================================ */
    .result-card {
        background: #0a0a0a;
        border: 2px solid #0000ff;
        border-radius: 0px;
        padding: 1.2rem;
        margin: 0.6rem 0;
        box-shadow: 4px 4px 0px #000080;
    }

    /* OCR text area — cyan on black */
    .ocr-area textarea {
        background: #0a0a0a !important;
        border: 2px solid #0000ff !important;
        border-radius: 0px !important;
        color: #00ffff !important;
        font-family: 'Courier New', monospace !important;
        font-size: 0.9rem !important;
        line-height: 1.8 !important;
        padding: 0.8rem !important;
    }

    /* Generated image display — pixel-blue frame, no artifacts */
    .stImage img {
        border-radius: 0px !important;
        border: 3px solid #0000ff !important;
        box-shadow:
            0 4px 24px rgba(0, 0, 255, 0.15),
            4px 4px 0px #000080 !important;
    }

    /* ================================================
       Buttons — black fill, blue pixel border
       ================================================ */
    .stButton > button {
        border-radius: 0px !important;
        font-family: 'Courier New', monospace !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em !important;
        border: 3px solid #0000ff !important;
        background: #0a0a0a !important;
        color: #ffffff !important;
        box-shadow: 4px 4px 0px #000080 !important;
        padding: 0.5rem 1.5rem !important;
        transition: none !important;
    }
    .stButton > button:hover {
        border-color: #4a90d9 !important;
        color: #ffffff !important;
        box-shadow:
            4px 4px 0px #1a3a5c,
            0 0 12px rgba(74, 144, 217, 0.2) !important;
    }
    .stButton > button:active {
        transform: translate(2px, 2px);
        box-shadow: 2px 2px 0px #000080 !important;
    }

    /* Expander panels */
    .streamlit-expanderHeader {
        border-radius: 0px !important;
        background: #0a0a0a !important;
        border: 2px solid #0000ff !important;
        font-family: 'Courier New', monospace !important;
        font-size: 0.82rem !important;
        color: #4a90d9 !important;
    }

    /* Status components */
    .stStatus {
        border-radius: 0px !important;
        border: 2px solid #0000ff !important;
        background: #0a0a0a !important;
        font-family: 'Courier New', monospace !important;
    }

    /* Dividers — pixel-blue thin line */
    hr {
        border: none !important;
        border-top: 1px solid #0000ff !important;
        margin: 1.6rem 0 !important;
        opacity: 0.5;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #333366;
        font-family: 'Courier New', monospace;
        font-size: 0.62rem;
        padding: 2.5rem 0 0.5rem;
        letter-spacing: 0.05em;
    }

    /* Scrollbar — pixel-blue narrow */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #000000; }
    ::-webkit-scrollbar-thumb {
        background: #0000ff;
        border-radius: 0px;
    }

    /* Chip labels — pixel style */
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
        background: #0a0a0a;
        border: 2px solid #00ffff;
        color: #00ffff;
    }
    .chip.art {
        background: #0a0a0a;
        border: 2px solid #ffb8ff;
        color: #ffb8ff;
    }

    /* Streamlit native notification bars */
    .stAlert {
        border-radius: 0px !important;
        border: 2px solid #0000ff !important;
        background: #0a0a0a !important;
        font-family: 'Courier New', monospace !important;
    }

    /* Mobile responsiveness */
    @media (max-width: 640px) {
        .main .block-container {
            padding: 1rem 1rem 3rem !important;
        }
        h1 {
            font-size: 1.4rem !important;
        }
        [data-testid="stFileUploadDropzone"] {
            padding: 1.5rem 1rem !important;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 🏠 Brand Header — refined, premium
# ============================================================
st.markdown(
    """
<h1>📖 VisionReader AI</h1>
<p class="subtitle">Snap a book page or upload an image to transform novel text into pixel art scenery.</p>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 📤 Upload Zone — clean, native, tactile
# ============================================================
upload_file = st.file_uploader(
    "Select Book Page (Takes photo via system rear-camera or choose from album)",
    type=["jpg", "jpeg", "png", "heic", "webp"],
    key=f"upload_{st.session_state.upload_key}",
    help="Supports JPG / PNG / HEIC / WebP formats. Mobile will invoke the native camera.",
    label_visibility="visible",
)

# ============================================================
# 🧠 Image Processing Pipeline — Pure OCR → Direct Pollinations
# ============================================================
if upload_file is not None:
    # Read image bytes
    img_bytes = upload_file.read()
    new_hash = hashlib.md5(img_bytes).hexdigest()

    # Only process on new image
    if new_hash != st.session_state.img_hash:
        st.session_state.img_hash = new_hash
        st.session_state.img_bytes = img_bytes
        st.session_state.show_results = False

        img = Image.open(io.BytesIO(img_bytes))
        st.session_state.img_width = img.width
        st.session_state.img_height = img.height

        # Book page snapshot preview (collapsed)
        with st.expander("👁️ View Book Page Snapshot", expanded=False):
            st.image(img, use_container_width=True)
            st.caption(f"Resolution: {img.width} × {img.height} px")

        # Main processing pipeline
        with st.status("🔍 Vision brain is parsing the book page...", expanded=True) as status:

            # ================================================
            # Stage 1: Gemini Pure OCR — extract Chinese text
            # ================================================
            st.write("🔍 **Stage 1/2: Extracting text from book page with precision...**")

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
                chinese_text = "OCR extraction failed. Please retry with a clearer book page photo."

            st.session_state.ocr_text = chinese_text

            # ================================================
            # Stage 2: Direct Pollinations — fixed seed 42520
            # ================================================
            if chinese_text:
                status.update(
                    label="🎨 Stage 2/2: Rendering text into visual pixel art...",
                    state="running",
                )

                final_prompt = chinese_text + STYLE_SUFFIX
                encoded_prompt = urllib.parse.quote(final_prompt, safe="")
                seed_num = 42520
                st.session_state.final_image_url = (
                    f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                    f"?width=1024&height=1536&nologo=true&seed={seed_num}"
                )

                status.update(
                    label="🎉 Rendering complete!", state="complete", expanded=False
                )
            else:
                status.update(label="⚠️ No valid text could be extracted", state="error")

            st.session_state.show_results = True

        # Rerun after processing to render results
        st.rerun()

    # ============================================================
    # 🖼️ Display Results
    # ============================================================
    if st.session_state.show_results:

        # Reset button
        def reset_all():
            st.session_state.upload_key += 1
            st.session_state.img_hash = ""
            st.session_state.img_bytes = None
            st.session_state.ocr_text = ""
            st.session_state.final_image_url = ""
            st.session_state.show_results = False

        st.button(
            "🔄 Scan New Page",
            on_click=reset_all,
            use_container_width=True,
            type="secondary",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Book page snapshot
        with st.expander("👁️ View Book Page Snapshot", expanded=False):
            img = Image.open(io.BytesIO(st.session_state.img_bytes))
            st.image(img, use_container_width=True)
            st.caption(
                f"Resolution: {st.session_state.img_width} × {st.session_state.img_height} px"
            )

        # ① OCR Extracted Text
        st.markdown("### 🔍 Extracted Book Text")
        if st.session_state.ocr_text:
            st.markdown(
                '<div class="result-card"><span class="chip ocr">OCR Result</span>',
                unsafe_allow_html=True,
            )
            st.text_area(
                "Extracted Book Text",
                value=st.session_state.ocr_text,
                height=200,
                key="ocr_display",
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No characters were detected in the image. Please ensure the book text is legible and retake the photo.")

        # ② AI Visual Rendering — full-width display
        if st.session_state.final_image_url:
            st.markdown("### 🎨 AI Visual Rendering")
            st.markdown(
                '<div style="text-align:center;margin:0.4rem 0 0.6rem;">'
                '<span class="chip art">Scene directly driven by your novel text.</span></div>',
                unsafe_allow_html=True,
            )
            st.image(
                st.session_state.final_image_url,
                caption="Visual realization of the book page text",
                use_container_width=True,
            )

            # Direct link
            with st.expander("🔗 Render Direct Link", expanded=False):
                st.code(st.session_state.final_image_url, language="text")

        # Error fallback
        if not st.session_state.ocr_text and not st.session_state.final_image_url:
            st.error(
                "VisionReader was unable to extract any valid text from the image. Please try:\n\n"
                "1. Ensure the book page is well-lit and the text is legible\n"
                "2. Position the camera directly above the page\n"
                "3. Use a higher-resolution image for upload"
            )

# ============================================================
# 🏠 Empty State Guide — clean pixel frame
# ============================================================
else:
    st.markdown(
        """
    <div style="text-align:center;padding:2.5rem 1.5rem;
                background:#0a0a0a;border-radius:0px;
                border:2px solid #0000ff;margin-top:0.5rem;
                box-shadow:4px 4px 0px #000080;">
        <div style="font-family:'Courier New',monospace;font-size:2.5rem;margin-bottom:0.8rem;
                    line-height:1;">📖</div>
        <div style="font-family:'Courier New',monospace;color:#4a90d9;font-size:0.82rem;line-height:2.0;">
            Upload or snap a page above.<br>
            Gemini will extract the text and render<br>
            your premium pixel art masterpiece synchronously.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ============================================================
# 📱 Footer
# ============================================================
st.markdown(
    """
<div class="footer">
    VisionReader AI · Pixel Book Reader<br>
    Powered by Gemini Vision &amp; Pollinations AI
</div>
""",
    unsafe_allow_html=True,
)
