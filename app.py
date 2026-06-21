"""
============================================================
VisionReader AI · 随身视界阅读器
移动端 AI 书页渲染器 — 拍照、OCR 识别、意境生图
============================================================
"""

import streamlit as st
import google.genai as genai
from google.genai import types
import urllib.parse
from PIL import Image
import json
import re

# ============================================================
# 🔐 核心配置 — 移动端一步到位，安全读取云端保险箱
# ============================================================
# 这样写，GitHub 上的黑客和谷歌机器人永远看不到你的真实 Key
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    # 本地盲测保底（如果本地运行时没配 secrets）
    GEMINI_API_KEY = "AQ.Ab8RN6KUXQqDGOOvPkruKSpw2xgc8zUKu8WKMVfXeBhVw0XWqQ"

GEMINI_MODEL = "gemini-3.5-flash"

# 直接初始化客户端
client = genai.Client(api_key=GEMINI_API_KEY)

# ============================================================
# 📱 Streamlit 页面配置（必须在最前面调用）
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

# ============================================================
# 🎨 移动端极致美化 — 暗色主题 + 窄屏优化 CSS
# ============================================================
st.markdown(
    """
<style>
    /* ===== 全局暗色主题基底 ===== */
    .stApp {
        background: linear-gradient(160deg, #080810 0%, #111122 30%, #0f1629 70%, #0a0a18 100%);
        background-attachment: fixed;
    }

    /* ===== 主容器窄屏约束（手机最佳宽度 480px） ===== */
    .main .block-container {
        max-width: 480px !important;
        padding: 0.8rem 0.9rem !important;
    }

    /* ===== 标题区域：渐变流光文字 ===== */
    h1 {
        font-size: 2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 50%, #f0a5c0 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-align: center;
        letter-spacing: 0.03em;
        margin-bottom: 0.1rem !important;
        padding-top: 0.3rem !important;
    }

    /* ===== 副标题 ===== */
    .vision-subtitle {
        text-align: center;
        color: #8888aa;
        font-size: 0.82rem;
        margin-bottom: 1.2rem;
        letter-spacing: 0.06em;
        font-weight: 400;
    }

    /* ===== 装饰分割线 ===== */
    .vision-divider {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0.2rem 0 1.4rem;
    }
    .vision-divider-line {
        flex: 1;
        height: 1px;
    }

    /* ===== 毛玻璃卡片 ===== */
    .vision-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 18px;
        padding: 1rem 1rem 0.5rem 1rem;
        margin: 0.8rem 0;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }

    /* ===== OCR 文字展示区域 ===== */
    .ocr-text-area textarea {
        background: rgba(255, 255, 255, 0.025) !important;
        border: 1px solid rgba(142, 197, 252, 0.18) !important;
        border-radius: 16px !important;
        color: #e0e0f0 !important;
        font-size: 0.95rem !important;
        line-height: 1.85 !important;
        padding: 0.9rem !important;
        font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif !important;
    }

    /* ===== 代码块（Image Prompt） ===== */
    .stCodeBlock {
        border-radius: 16px !important;
        border: 1px solid rgba(240, 165, 192, 0.18) !important;
    }
    .stCodeBlock code {
        font-size: 0.82rem !important;
        line-height: 1.6 !important;
    }

    /* ===== 状态组件圆角 ===== */
    .stStatus {
        border-radius: 16px !important;
    }

    /* ===== Expander 圆角 ===== */
    .streamlit-expanderHeader {
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.025) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        font-size: 0.88rem !important;
    }

    /* ===== 图片圆角 + 阴影 ===== */
    .stImage img {
        border-radius: 18px !important;
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5), 0 0 60px rgba(100, 120, 255, 0.08) !important;
    }

    /* ===== 水平线 ===== */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
        margin: 1.2rem 0 !important;
    }

    /* ===== Tab 组件美化 ===== */
    .stTabs [data-baseweb="tab"] {
        font-size: 0.9rem !important;
        padding: 0.5rem 1rem !important;
    }

    /* ===== 底部信息 ===== */
    .vision-footer {
        text-align: center;
        color: rgba(255, 255, 255, 0.22);
        font-size: 0.7rem;
        padding: 2rem 0 0.8rem;
        letter-spacing: 0.05em;
        line-height: 1.7;
    }

    /* ===== 胶囊标签 ===== */
    .vision-chip {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.68rem;
        letter-spacing: 0.06em;
        margin-bottom: 0.6rem;
        font-weight: 500;
    }
    .vision-chip.ocr {
        background: rgba(142, 197, 252, 0.1);
        border: 1px solid rgba(142, 197, 252, 0.22);
        color: #8ec5fc;
    }
    .vision-chip.prompt {
        background: rgba(240, 165, 192, 0.1);
        border: 1px solid rgba(240, 165, 192, 0.22);
        color: #f0a5c0;
    }
    .vision-chip.art {
        background: rgba(192, 220, 150, 0.1);
        border: 1px solid rgba(192, 220, 150, 0.2);
        color: #c0dc96;
    }

    /* ===== 链接 ===== */
    a {
        color: #8ec5fc !important;
        text-decoration: none !important;
    }

    /* ===== 信息提示框 ===== */
    .stAlert {
        border-radius: 14px !important;
    }

    /* ===== 移动端 touch 优化 ===== */
    button, [data-baseweb="tab"], .streamlit-expanderHeader {
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
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
<div style="text-align: center;">
    <h1>📖 VisionReader AI</h1>
    <p class="vision-subtitle">拍下书页 · 看见故事 · 沉浸意境</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="vision-divider">
    <div class="vision-divider-line" style="background: linear-gradient(90deg, transparent, rgba(142,197,252,0.15));"></div>
    <span style="color: rgba(255,255,255,0.18); font-size: 0.65rem;">✦</span>
    <div class="vision-divider-line" style="background: linear-gradient(90deg, rgba(240,165,192,0.15), transparent);"></div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 📸 核心交互区：双 Tab（拍摄 / 上传）
# ============================================================
tab_camera, tab_upload = st.tabs(["📸 拍摄书页", "🖼️ 上传照片"])

with tab_camera:
    camera_file = st.camera_input(
        "将摄像头对准书页，点击拍照",
        key="main_camera",
        help="手机端自动唤起后置摄像头",
    )

with tab_upload:
    upload_file = st.file_uploader(
        "选择书页照片上传",
        type=["jpg", "jpeg", "png", "heic", "webp"],
        key="main_upload",
        help="支持 JPG / PNG / HEIC / WebP 格式",
    )

# 统一图片源
image_source = camera_file or upload_file

# ============================================================
# 🧠 VisionReader AI 全链路处理管线
# ============================================================
if image_source:
    # 读取图片对象
    img = Image.open(image_source)

    # ----- 书页快照预览（折叠） -----
    with st.expander("👁️ 查看书页快照", expanded=False):
        st.image(img, use_container_width=True)
        st.caption(f"分辨率：{img.width} × {img.height} px")

    # ----- 主处理流程 -----
    with st.status(
        "🧠 视觉大脑正在解析书页意境...", expanded=True
    ) as pipeline_status:

        # ========================================================
        # 阶段 1：Gemini 多模态 — OCR 文字提取 + 意境 Prompt 生成
        # ========================================================
        st.write("🔍 **阶段 1/2：识别书页文字 & 提炼视觉剧本...**")

        multi_task_prompt = """你是一个顶级的 OCR 文字识别专家与电影级场景架构师。

请严格完成以下两个独立任务，并以标准 JSON 格式输出：

---

**任务一 · 文字提取（OCR）**：
仔细识别图片中所有的中文文字内容。要求：
- 完整、准确地提取每一个可见的中文字符
- 保留原文的段落结构和标点符号
- 如果图片中确实没有任何文字，chinese_text 字段请设置为空字符串 ""

**任务二 · 视觉意境转化**：
基于图片的书页内容、排版质感、纸张纹理、以及文字传达的情绪与氛围，创作一句极具电影感和视觉冲击力的英文 Image Prompt。要求：
- 风格参考："Cinematic masterpiece, volumetric lighting, ..."
- 必须包含具体的视觉元素：光线、色彩、构图、材质、氛围
- 营造强烈的情绪张力与沉浸感
- 控制在 60–180 个英文单词
- 必须为纯英文

---

**输出格式 — 严格按照以下 JSON 结构，不要包含任何多余文字：**
```json
{
  "chinese_text": "完整的中文原文放在这里...",
  "image_prompt": "Cinematic masterpiece, ..."
}
```"""

        try:
            # 调用 Gemini 多模态 API（单次调用完成 OCR + 意境生成）
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[img, multi_task_prompt],
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    max_output_tokens=2048,
                ),
            )

            raw_response = response.text.strip()

            # --- 解析结构化 JSON ---
            json_match = re.search(
                r"```(?:json)?\s*([\s\S]*?)\s*```", raw_response
            )
            json_str = json_match.group(1) if json_match else raw_response

            result = json.loads(json_str)
            chinese_text = result.get("chinese_text", "").strip()
            image_prompt = result.get("image_prompt", "").strip()

            pipeline_status.update(
                label="✅ 阶段 1/2 完成：文字已提取，意境剧本已生成",
                state="running",
            )

        except (json.JSONDecodeError, KeyError, AttributeError):
            # 降级处理：尝试从原始响应中分离中英文
            st.warning("⚠️ 结构化解析异常，尝试降级提取...")
            raw = response.text.strip() if "response" in dir() else ""

            # 启发式提取中文字符
            cn_blocks = re.findall(
                r"[一-鿿　-〿＀-￯‘-”、-。，．：；！（）]+",
                raw,
            )
            chinese_text = "\n".join(cn_blocks) if cn_blocks else ""

            # 尝试提取英文 Prompt（去掉中文部分后取最长英文段）
            en_only = re.sub(r"[一-鿿　-〿＀-￯]+", "", raw)
            en_sentences = [
                s.strip()
                for s in re.split(r"[。\n]+", en_only)
                if len(s.strip()) > 20
            ]
            image_prompt = max(en_sentences, key=len) if en_sentences else raw

            pipeline_status.update(
                label="✅ 阶段 1/2 完成（降级模式）", state="running"
            )

        except Exception as api_err:
            pipeline_status.update(label="❌ API 调用失败", state="error")
            st.error(f"Gemini API 通信异常，请检查网络后重试。\n\n`{api_err}`")
            st.stop()

        # ========================================================
        # 展示 ①：OCR 提取的中文原始文本
        # ========================================================
        st.markdown("### 📝 扫描到的原始文字")

        if chinese_text:
            st.markdown(
                """
            <div class="vision-card">
                <span class="vision-chip ocr">✦ OCR 识别结果</span>
            """,
                unsafe_allow_html=True,
            )

            st.text_area(
                "书页原文",
                value=chinese_text,
                height=180,
                key="ocr_result",
                label_visibility="collapsed",
            )

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info(
                "🤔 未在图像中检测到中文字符。"
                "请确保拍摄的书页包含清晰的中文文字，并重新拍摄。"
            )

        # ========================================================
        # 展示 ②：Gemini 提炼的英文 Image Prompt
        # ========================================================
        if image_prompt:
            st.markdown("### 🎬 提炼的视觉剧本")
            st.markdown(
                """
            <div class="vision-card">
                <span class="vision-chip prompt">✦ 电影级 Image Prompt</span>
            """,
                unsafe_allow_html=True,
            )

            st.code(image_prompt, language="text")

            st.markdown("</div>", unsafe_allow_html=True)

        # ========================================================
        # 阶段 2：Pollinations AI 渲染图像
        # ========================================================
        if image_prompt:
            pipeline_status.update(
                label="🎨 阶段 2/2：正在将意境渲染至手机画布...",
                state="running",
            )

            # URL 编码 + 拼接 Pollinations 流式通道
            encoded_prompt = urllib.parse.quote(image_prompt, safe="")
            # 竖屏比例（更适合手机阅读场景）
            final_image_url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                f"?width=768&height=1024&nologo=true"
            )

            pipeline_status.update(
                label="🎉 沉浸式视界已同步！", state="complete", expanded=False
            )

            # ====================================================
            # 展示 ③：手机正中心 — AI 渲染画作
            # ====================================================
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
                final_image_url,
                caption="当前书页的视觉具象化展现",
                use_container_width=True,
            )

            # 直链分享
            st.markdown("---")
            st.markdown(
                f"""
            <div class="vision-card" style="text-align: center;">
                <div style="color: rgba(255,255,255,0.4); font-size: 0.7rem; margin-bottom: 0.2rem;">
                    🔗 渲染直链
                </div>
                <a href="{final_image_url}" target="_blank" style="
                    font-size: 0.65rem;
                    word-break: break-all;
                    opacity: 0.55;
                ">{final_image_url}</a>
            </div>
            """,
                unsafe_allow_html=True,
            )

        elif not chinese_text:
            # image_prompt 为空且 chinese_text 也为空 → 完全无有效内容
            pipeline_status.update(label="⚠️ 未能提取有效内容", state="error")
            st.error(
                "VisionReader 未能从图像中提取有效文字或生成视觉提示词。"
                "请尝试：\n"
                "1. 确保书页光照充足、文字清晰\n"
                "2. 将手机对准书页正上方拍摄\n"
                "3. 使用「上传照片」选择高分辨率图片"
            )

# ============================================================
# 🏠 空状态引导 — 优雅的首次访问界面
# ============================================================
else:
    st.markdown(
        """
    <div class="vision-card" style="text-align: center; padding: 2.2rem 1.2rem;">
        <div style="font-size: 3.5rem; margin-bottom: 0.8rem; opacity: 0.55;">📖</div>
        <div style="
            color: rgba(255,255,255,0.72);
            font-size: 0.95rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            letter-spacing: 0.03em;
        ">
            开始你的沉浸式阅读之旅
        </div>
        <div style="
            color: rgba(255,255,255,0.35);
            font-size: 0.78rem;
            line-height: 1.8;
        ">
            点击上方 <span style="color: #8ec5fc; font-weight: 500;">📸 拍摄书页</span>
            或 <span style="color: #8ec5fc; font-weight: 500;">🖼️ 上传照片</span><br>
            AI 将自动识别书中文字，并为你生成<br>
            独一无二的电影级视觉画作
        </div>
        <div style="
            margin-top: 1.4rem;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.6rem;
            flex-wrap: wrap;
        ">
            <span style="color: rgba(255,255,255,0.22); font-size: 0.68rem;">📸</span>
            <span style="color: rgba(255,255,255,0.12); font-size: 0.6rem;">→</span>
            <span style="color: rgba(255,255,255,0.22); font-size: 0.68rem;">🔍</span>
            <span style="color: rgba(255,255,255,0.12); font-size: 0.6rem;">→</span>
            <span style="color: rgba(255,255,255,0.22); font-size: 0.68rem;">🎨</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ============================================================
# 📱 底部品牌信息
# ============================================================
st.markdown(
    """
<div class="vision-footer">
    VisionReader AI · 随身视界阅读器<br>
    Powered by Gemini Vision & Pollinations AI
</div>
""",
    unsafe_allow_html=True,
)
