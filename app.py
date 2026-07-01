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

# Pollinations fixed quality suffix — landscape-first epic composition
# v8.0: Geology-centric guard — environment dominates, subjects are accents
STYLE_SUFFIX = (
    ", An immense and spectacular conceptual masterpiece, groundbreaking epic landscape driven primarily by the described geology or background, grand scale composition, text-described subjects or creatures must be secondary, subtle accents, less than 10% in frame size, NO humans unless explicitly named, hyper-detailed, epic lighting, dark atmospheric aesthetic, masterpiece, 8k resolution, cinematic, NO close-up"
)

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
       Upload Zone — Pixel Camera Entry
       v8.0: Native DOM fully hidden; custom retro icons
       ================================================ */

    /* Outer container: black box, blue pixel border */
    [data-testid="stFileUploader"] {
        position: relative !important;
        background: #000000 !important;
        border: 3px solid #0000ff !important;
        border-radius: 0px !important;
        padding: 2.5rem 1.5rem !important;
        text-align: center !important;
        min-height: 130px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Custom pixel camera entry: 📸 + 🖼️ icons, single clean label */
    [data-testid="stFileUploader"]::before {
        content: "📸  🖼️\\A Scan or Upload";
        white-space: pre !important;
        font-family: 'Courier New', monospace !important;
        font-size: 1.3rem !important;
        color: #ffffff !important;
        letter-spacing: 0.06em !important;
        display: block !important;
        text-align: center !important;
        line-height: 2 !important;
    }

    /* Brutal Fix: hide ALL native children of stFileUploader */
    [data-testid="stFileUploader"] > label {
        display: none !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploadDropzone"] button {
        display: none !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploadDropzone"] [data-testid="stMarkdownContainer"] {
        display: none !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploadDropzone"] small {
        display: none !important;
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploadDropzone"] div {
        display: none !important;
    }

    /* Make dropzone invisible but still clickable as overlay */
    [data-testid="stFileUploadDropzone"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        cursor: pointer !important;
        z-index: 10 !important;
        border: none !important;
        background: transparent !important;
        border-radius: 0px !important;
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
        [data-testid="stFileUploader"] {
            padding: 1.5rem 1rem !important;
        }
        [data-testid="stFileUploader"]::before {
            font-size: 1rem !important;
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
    "Select Book Page",
    type=["jpg", "jpeg", "png", "heic", "webp"],
    key=f"upload_{st.session_state.upload_key}",
    help="Supports JPG / PNG / HEIC / WebP formats.",
    label_visibility="collapsed",
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
        with st.status("📖 Reading page…", expanded=True) as status:

            # ================================================
            # Phase 1: Pure Gemini OCR Extraction
            # ================================================
            st.write("🔍 Extracting Text...")

            ocr_prompt = """You are an expert OCR specialist. Your sole task is to accurately recognize and extract all visible Chinese text from this image.

Rules:
1. Maintain the original paragraph structure, line breaks, and punctuation exactly.
2. If no Chinese text is detected in the image, return an empty string.
3. Do not add any extra explanations, notes, or contextual commentary.
4. Do not translate the text; perform pure, literal OCR extraction.

Return a JSON object containing a single key "chinese_text" holding the extracted content."""

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
                    label="🎨 Generating Imagery...",
                    state="running",
                )

                final_prompt = chinese_text[:150] + STYLE_SUFFIX
                encoded_prompt = urllib.parse.quote(final_prompt, safe="")
                seed_num = 42520
                st.session_state.final_image_url = (
                    f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                    f"?width=1024&height=1536&nologo=true&seed={seed_num}"
                )

                status.update(
                    label="✅ Done", state="complete", expanded=False
                )
            else:
                status.update(label="⚠️ No text", state="error")

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

        # ① OCR Extracted Text
        st.markdown("### 🔍 Extracted Book Text")
        if st.session_state.ocr_text:
            st.text_area(
                "Extracted Book Text",
                value=st.session_state.ocr_text,
                height=200,
                key="ocr_display",
                label_visibility="collapsed",
            )
        else:
            st.info("No characters were detected in the image. Please ensure the book text is legible and retake the photo.")

        # ② AI Visual Rendering — clean title → subtitle → full-width image
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
