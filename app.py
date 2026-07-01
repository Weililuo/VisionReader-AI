"""
============================================================
VisionReader AI · Art Scenery Book Reader  v7.0  Final
HD Upload → Pure OCR → Direct Pollinations Image Generation
Style: Dark Cinematic · Conceptual Masterpiece Render
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

# Pollinations style suffix — disabled; using pure text only for authentic alignment
STYLE_SUFFIX = ""

# ============================================================
# 📱 Streamlit Page Configuration
# ============================================================
st.set_page_config(
    page_title="VisionReader AI · Art Reader",
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
# 🎨 Ultimate Dark Cinematic CSS — Art Scenery Theme
# ============================================================
st.markdown(
    """
<style>
    /* ================================================
       VisionReader AI · Art Scenery Theme
       Pure black · Electric-blue accents · Cinematic
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

    /* Brand title — clean monospace white */
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

    /* Global body — monospace */
    body, p, div, span, label, button, input, textarea, caption, .stMarkdown {
        font-family: 'Courier New', monospace !important;
    }

    /* Subtitle / tagline — electric blue, one clean line */
    .subtitle {
        text-align: center;
        color: #4a90d9;
        font-size: 0.88rem;
        margin-bottom: 1.5rem;
        letter-spacing: 0.04em;
    }

    /* ================================================
       🎞️ Visual Showcase Marquee — Infinite Scroll
       ================================================ */
    .marquee-outer {
        width: 100%;
        overflow: hidden;
        overflow-x: hidden;
        position: relative;
        height: 140px;
        margin-bottom: 2rem;
        background: #000000;
    }
    .marquee-outer::before,
    .marquee-outer::after {
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        width: 40px;
        z-index: 2;
        pointer-events: none;
    }
    .marquee-outer::before {
        left: 0;
        background: linear-gradient(to right, #000000 0%, transparent 100%);
    }
    .marquee-outer::after {
        right: 0;
        background: linear-gradient(to left, #000000 0%, transparent 100%);
    }
    .marquee-track {
        display: flex;
        position: absolute;
        animation: marquee-scroll 30s linear infinite;
        width: max-content;
        white-space: nowrap;
        will-change: transform;
    }
    .marquee-track img {
        height: 130px;
        width: auto;
        margin: 5px 6px;
        object-fit: cover;
        clip-path: inset(0 0 0 0);
        border: 2px solid #0000ff;
        flex-shrink: 0;
        display: inline-block;
    }
    @keyframes marquee-scroll {
        0%   { transform: translateX(0); }
        100% { transform: translateX(-50%); }
    }

    /* ================================================
       📸 Upload Zone — Centered Camera UI
       Pure visual touch sensor, no text clutter
       ================================================ */

    /* ──  Obliterate ALL native text inside upload component  ── */
    div[data-testid="stFileUploader"] section button div,
    div[data-testid="stFileUploadDropzone"] div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stFileUploadDropzone"] small,
    div[data-testid="stFileUploader"] label {
        display: none !important;
    }

    /* Dropzone — dark canvas with blue border */
    [data-testid="stFileUploadDropzone"] {
        border-radius: 0px !important;
        border: 3px solid #0000ff !important;
        background: #0a0a0a !important;
        padding: 0px !important;
    }

    /* ──  Centered camera button — the only visible element  ── */
    div[data-testid="stFileUploader"] section button {
        background-color: #0a0a0a !important;
        border: 3px solid #0000ff !important;
        border-radius: 0px !important;
        padding: 3.5rem 1.5rem !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
    }

    /* 📸 Camera icon + "Snap or Upload" — perfectly centered */
    div[data-testid="stFileUploader"] section button::after {
        content: "📸\a\aSnap or Upload" !important;
        white-space: pre-wrap !important;
        text-align: center !important;
        font-family: 'Courier New', monospace !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        color: #ffffff !important;
        letter-spacing: 0.05em !important;
    }

    /* ================================================
       Result Cards — electric-blue rectilinear border
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

    /* Generated image display — electric-blue frame */
    .stImage img {
        border-radius: 0px !important;
        border: 3px solid #0000ff !important;
        box-shadow:
            0 4px 24px rgba(0, 0, 255, 0.15),
            4px 4px 0px #000080 !important;
    }

    /* ================================================
       Buttons — black fill, blue border
       ================================================ */
    .stButton > button {
        border-radius: 0px !important;
        font-family: 'Courier New', monospace !important;
        font-weight: 900 !important;
        font-size: 1.25rem !important;
        letter-spacing: 0.08em !important;
        border: 4px solid #0000ff !important;
        background: #0a0a0a !important;
        color: #ffffff !important;
        padding: 1.2rem 2.5rem !important;
        box-shadow: 0px 8px 0px #000080 !important;
        width: 100%;
        transition: all 0.1s ease !important;
        cursor: pointer;
    }
    .stButton > button:hover {
        border-color: #4a90d9 !important;
        background: #0d0d1a !important;
        box-shadow: 0px 8px 0px #1a3a5c !important;
    }
    .stButton > button:active {
        transform: translate3d(0, 6px, 0) !important;
        box-shadow: 0px 2px 0px #000080 !important;
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

    /* Dividers — electric-blue thin line */
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

    /* Scrollbar — electric-blue narrow */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #000000; }
    ::-webkit-scrollbar-thumb {
        background: #0000ff;
        border-radius: 0px;
    }

    /* Chip labels */
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
        div[data-testid="stFileUploader"] section button {
            padding: 2rem 1rem !important;
        }
        div[data-testid="stFileUploader"] section button::after {
            font-size: 0.9rem !important;
        }
        .marquee-outer {
            height: 120px;
            margin-bottom: 1.4rem;
            overflow-x: hidden;
        }
        .marquee-track img {
            height: 110px;
            display: inline-block;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 🏠 Brand Header — refined art scenery
# ============================================================
st.markdown(
    """
<h1>📖 VisionReader AI</h1>
<p class="subtitle">Snap a book page or upload an image to transform novel text into art scenery.</p>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 🎞️ Visual Showcase — Infinite Horizontal Marquee
#    Pollinations AI pre-generated cinematic concept art
# ============================================================
MARQUEE_IMAGES = [
    "https://image.pollinations.ai/prompt/beautiful-fantasy-castle-on-floating-island-at-sunset?width=300&height=200&nologo=true&seed=12345",
    "https://image.pollinations.ai/prompt/epic-fantasy-ranger-knight-standing-in-snowy-forest?width=300&height=200&nologo=true&seed=23456",
    "https://image.pollinations.ai/prompt/A%20magnificent%20mystical%20dragon%20perched%20on%20a%20glowing%20crystal%20mountain,%20epic%20lighting?width=300&height=200&nologo=true&seed=777",
    "https://image.pollinations.ai/prompt/cyberpunk-city-street-with-bright-neon-lights-at-night?width=300&height=200&nologo=true&seed=34567",
    "https://image.pollinations.ai/prompt/glowing-ancient-magical-crystal-floating-in-dark-sanctuary?width=300&height=200&nologo=true&seed=45678",
]

marquee_img_tags = "\n".join(
    f'<img src="{url}" alt="AI Concept Art" loading="lazy" />'
    for url in MARQUEE_IMAGES
)

st.markdown(
    f"""
<div class="marquee-outer">
    <div class="marquee-track">
        {marquee_img_tags}
        {marquee_img_tags}
    </div>
</div>
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

        # Main processing pipeline
        with st.status("📖 Reading Page...", expanded=True) as status:

            # ================================================
            # Stage 1: Gemini Pure OCR — extract Chinese text
            # ================================================
            st.write("🔍 Extracting Text...")

            ocr_prompt = """Your sole task is to accurately recognize and extract all visible Chinese text from this image.

Rules:
1. Preserve the original paragraph structure, line breaks, and punctuation exactly as they appear.
2. If there is no Chinese text in the image, return an empty string.
3. Do not add any explanations, commentary, or extra content of any kind.
4. Do not translate, do not summarize — perform pure OCR extraction only.

Return a JSON object with a single key "chinese_text" whose value is all the Chinese text you recognized."""

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
                    label="🎨 Rendering Scenery...",
                    state="running",
                )

                # Truncate to 150 chars maximum to prevent URL-overlength bugs
                truncated_text = chinese_text[:150]
                final_prompt = truncated_text
                encoded_prompt = urllib.parse.quote(final_prompt, safe="")
                seed_num = 42520
                st.session_state.final_image_url = (
                    f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                    f"?width=1024&height=1536&nologo=true&seed={seed_num}"
                )

                status.update(
                    label="🎉 Render Complete!", state="complete", expanded=False
                )
            else:
                status.update(label="⚠️ No valid text could be extracted", state="error")

            st.session_state.show_results = True

        # Rerun after processing to render results
        st.rerun()

    # ============================================================
    # 🖼️ Display Results — Three-box merge: uploader vanishes,
    #    "Scan New Page" button takes its place in situ.
    # ============================================================
    if st.session_state.show_results:

        # Dynamically hide the file uploader so the button replaces it visually
        st.markdown(
            """
        <style>
            div[data-testid="stFileUploader"] {
                display: none !important;
            }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Reset callback
        def reset_all():
            st.session_state.upload_key += 1
            st.session_state.img_hash = ""
            st.session_state.img_bytes = None
            st.session_state.ocr_text = ""
            st.session_state.final_image_url = ""
            st.session_state.show_results = False

        # "Scan New Page" — sits exactly where the uploader was, full-width rectilinear key
        st.button(
            "🔄 Scan New Page",
            on_click=reset_all,
            use_container_width=True,
            type="secondary",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ① OCR Extracted Text
        if st.session_state.ocr_text:
            st.markdown(
                '<div class="result-card">',
                unsafe_allow_html=True,
            )
            st.text_area(
                "🔍 Extracted Book Text  ·  🖼️ Art rendering ready below.",
                value=st.session_state.ocr_text,
                height=200,
                key="ocr_display",
                label_visibility="visible",
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No characters were detected in the image. Please ensure the book text is legible and retake the photo.")

        # ② AI Visual Rendering — full-width display
        if st.session_state.final_image_url:
            st.markdown("### 🎨 AI Visual Rendering")
            st.image(
                st.session_state.final_image_url,
                use_container_width=True,
            )

        # Error fallback
        if not st.session_state.ocr_text and not st.session_state.final_image_url:
            st.error(
                "VisionReader was unable to extract any valid text from the image. Please try:\n\n"
                "1. Ensure the book page is well-lit and the text is legible\n"
                "2. Position the camera directly above the page\n"
                "3. Use a higher-resolution image for upload"
            )

# ============================================================
# 🏠 Empty State Guide — clean frame, single line only
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
        <div style="font-family:'Courier New',monospace;color:#4a90d9;font-size:0.82rem;">
            Upload or snap a page above.
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
    VisionReader AI · Art Scenery Book Reader<br>
    Powered by Gemini Vision &amp; Pollinations AI
</div>
""",
    unsafe_allow_html=True,
)
