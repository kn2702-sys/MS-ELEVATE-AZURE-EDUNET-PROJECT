import logging
# Suppress Streamlit label warnings BEFORE importing streamlit
logging.getLogger("streamlit.elements.lib.policies").setLevel(logging.ERROR)
logging.getLogger("streamlit").setLevel(logging.ERROR)

import streamlit as st
import os
import json
import re
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from io import StringIO

try:
    from dotenv import load_dotenv
    load_dotenv()
    HAS_DOTENV = True
except ModuleNotFoundError:
    HAS_DOTENV = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ModuleNotFoundError:
    HAS_OPENAI = False

try:
    from PyPDF2 import PdfReader
    HAS_PDF = True
except ModuleNotFoundError:
    HAS_PDF = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ModuleNotFoundError:
    HAS_BS4 = False


# =========================================================
# CONFIGURATION & DARK THEME
# =========================================================
st.set_page_config(
    page_title="Elevate AI Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

DARK_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg-primary: #0b0f19;
        --bg-secondary: #111827;
        --bg-card: #151c2c;
        --bg-elevated: #1e293b;
        --border: rgba(148, 163, 184, 0.1);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent: #34d399;
        --accent-glow: rgba(52, 211, 153, 0.15);
        --accent-hover: #10b981;
        --success: #34d399;
        --warning: #fbbf24;
        --danger: #f87171;
        --gradient-start: #34d399;
        --gradient-end: #059669;
    }

    .stApp {
        background: var(--bg-primary);
        font-family: 'Inter', sans-serif;
    }

    .main .block-container {
        background: var(--bg-primary);
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    p, li, span, div {
        color: var(--text-secondary);
    }

    .glass-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6) 0%, rgba(21, 28, 44, 0.8) 100%);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .glass-card:hover {
        border-color: rgba(52, 211, 153, 0.3);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 0 20px var(--accent-glow);
        transform: translateY(-2px);
    }

    .stButton>button {
        background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
        letter-spacing: 0.01em;
    }
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4) !important;
        filter: brightness(1.1);
    }
    .stButton>button:active {
        transform: translateY(0) scale(0.98);
    }

    button[kind="secondary"] {
        background: transparent !important;
        color: var(--accent) !important;
        border: 1.5px solid var(--accent) !important;
        box-shadow: none !important;
    }
    button[kind="secondary"]:hover {
        background: var(--accent-glow) !important;
    }

    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stNumberInput>div>div>input {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
    }
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }
    
    .stTextArea textarea {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }

    .stSelectbox>div>div {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }
    .stSelectbox>div>div>div {
        color: var(--text-primary) !important;
    }

    .stSlider>div>div>div {
        background: var(--accent) !important;
    }
    .stSlider>div>div>div>div {
        background: white !important;
    }

    .stFileUploader>div>div>div {
        background: var(--bg-secondary) !important;
        border: 2px dashed var(--border) !important;
        border-radius: 12px !important;
        color: var(--text-secondary) !important;
    }
    .stFileUploader>div>div>div:hover {
        border-color: var(--accent) !important;
        background: var(--accent-glow) !important;
    }

    .chat-user {
        background: linear-gradient(135deg, rgba(52, 211, 153, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%);
        border-left: 3px solid var(--accent);
        padding: 1rem 1.25rem;
        border-radius: 4px 16px 16px 16px;
        margin: 0.75rem 0;
        color: var(--text-primary);
        border: 1px solid rgba(52, 211, 153, 0.1);
    }
    .chat-assistant {
        background: var(--bg-elevated);
        border-left: 3px solid var(--success);
        padding: 1rem 1.25rem;
        border-radius: 4px 16px 16px 16px;
        margin: 0.75rem 0;
        color: var(--text-primary);
        border: 1px solid var(--border);
    }

    div[role="radiogroup"] label {
        background: var(--bg-secondary);
        padding: 1rem 1.25rem;
        border-radius: 12px;
        border: 1.5px solid var(--border);
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s;
        width: 100%;
        color: var(--text-secondary) !important;
    }
    div[role="radiogroup"] label:hover {
        border-color: var(--accent);
        background: rgba(52, 211, 153, 0.05);
        color: var(--text-primary) !important;
    }
    div[role="radiogroup"] label[data-baseweb="radio"] div[aria-checked="true"] {
        background: var(--accent) !important;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, var(--accent) 0%, var(--gradient-end) 100%) !important;
        border-radius: 10px;
        box-shadow: 0 0 10px var(--accent-glow);
    }

    .dataframe {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
    }
    .dataframe th {
        background: var(--bg-elevated) !important;
        color: var(--accent) !important;
        font-weight: 600 !important;
        border-bottom: 1px solid var(--border) !important;
    }
    .dataframe td {
        color: var(--text-secondary) !important;
        border-bottom: 1px solid var(--border) !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0f172a 100%) !important;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-secondary) !important;
    }
    [data-testid="stSidebar"] .stButton>button {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--border) !important;
        box-shadow: none !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: var(--bg-card) !important;
        border-color: var(--accent) !important;
    }

    /* Sidebar metric styling */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #34d399 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stSidebar"] [data-testid="stMetricDelta"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bg-secondary);
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--bg-elevated) !important;
        color: var(--accent) !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3) !important;
    }

    .streamlit-expanderHeader {
        background: var(--bg-secondary) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }
    .streamlit-expanderContent {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        color: var(--text-secondary) !important;
    }

    .stSuccess {
        background: rgba(52, 211, 153, 0.1) !important;
        border: 1px solid rgba(52, 211, 153, 0.2) !important;
        border-radius: 12px !important;
        color: var(--success) !important;
    }
    .stInfo {
        background: rgba(52, 211, 153, 0.1) !important;
        border: 1px solid rgba(52, 211, 153, 0.2) !important;
        border-radius: 12px !important;
        color: var(--accent) !important;
    }
    .stInfo p, .stInfo div {
        color: var(--text-primary) !important;
    }
    .stWarning {
        background: rgba(251, 191, 36, 0.1) !important;
        border: 1px solid rgba(251, 191, 36, 0.2) !important;
        border-radius: 12px !important;
        color: var(--warning) !important;
    }
    .stError {
        background: rgba(248, 113, 113, 0.1) !important;
        border: 1px solid rgba(248, 113, 113, 0.2) !important;
        border-radius: 12px !important;
        color: var(--danger) !important;
    }

    hr {
        border-color: var(--border) !important;
        opacity: 0.5;
    }

    .stCaption {
        color: var(--text-muted) !important;
    }

    .footer {
        text-align: center;
        padding: 2rem;
        color: var(--text-muted);
        font-size: 0.875rem;
        border-top: 1px solid var(--border);
        margin-top: 3rem;
    }

    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--bg-elevated);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }

    [data-testid="stMetricValue"] {
        color: var(--accent) !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
    }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)


# =========================================================
# API CLIENT SETUP
# =========================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

if not OPENROUTER_API_KEY:
    OPENROUTER_API_KEY = st.sidebar.text_input("🔑 OpenRouter API Key", type="password", key="api_key_input")

client: Optional[object] = None
if OPENROUTER_API_KEY and HAS_OPENAI:
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

MODEL_NAME = "openrouter/auto"


# =========================================================
# SESSION STATE
# =========================================================
def init_state():
    defaults = {
        "text_content": "",
        "text_summary": "",
        "quiz_questions": [],
        "answers": {},
        "quiz_score": None,
        "quiz_submitted": False,
        "quiz_history": [],
        "chat_history": [],
        "analytics": {"quizzes_taken": 0, "total_score": 0, "total_questions": 0},
        "last_activity": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# =========================================================
# UTILITY FUNCTIONS
# =========================================================
def estimate_reading_time(text: str) -> str:
    words = len(text.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min"


def calculate_content_stats(text: str) -> Dict:
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    return {
        "characters": len(text),
        "words": len(words),
        "sentences": len([s for s in sentences if s.strip()]),
        "paragraphs": len(paragraphs),
        "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 1),
        "reading_time": estimate_reading_time(text)
    }


def extract_text(file) -> str:
    if file is None:
        return ""
    file_name = getattr(file, "name", "").lower()
    content = ""
    try:
        if file.type == "text/plain" or file_name.endswith(".txt"):
            content = file.read().decode("utf-8", errors="ignore")
        elif file.type == "application/pdf" or file_name.endswith(".pdf"):
            if not HAS_PDF:
                st.error("📄 PyPDF2 not installed. Run: `pip install PyPDF2`")
                return ""
            reader = PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    content += page_text + "\n\n"
        elif file.type in ["text/html", "application/octet-stream"] or file_name.endswith((".html", ".htm")):
            if not HAS_BS4:
                st.error("🌐 BeautifulSoup not installed. Run: `pip install beautifulsoup4`")
                return ""
            soup = BeautifulSoup(file.read(), "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()
            content = soup.get_text(separator="\n", strip=True)
        else:
            content = file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""
    return content.strip()[:25000]


def clear_quiz_keys():
    for key in list(st.session_state.keys()):
        if key.startswith("question_"):
            del st.session_state[key]


def generate_summary(text: str) -> str:
    if not client:
        return "API key required for summarization."
    if not text.strip():
        return "No content to summarize."
    try:
        prompt = f"""Provide a concise, professional summary (3-4 bullet points) of the following content. 
Focus on key concepts, main arguments, and important takeaways.

CONTENT:
{text[:6000]}

Format as markdown bullet points."""
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert educator who creates clear, structured summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Summary generation failed: {e}"


def generate_explanation(question: str, difficulty: str, context: str) -> str:
    if not client:
        return "⚠️ Please configure your OpenRouter API key in the sidebar."
    if not question.strip():
        return "Please enter a valid question."
    history = st.session_state.chat_history[-10:]
    messages = [
        {
            "role": "system",
            "content": (
                f"You are an expert tutor. Explain concepts at a {difficulty.lower()} level "
                f"using clear language, relevant examples, and structured formatting. "
                f"Reference the provided material when applicable.\n\n"
                f"MATERIAL CONTEXT:\n{context[:4000]}"
            )
        }
    ] + history + [{"role": "user", "content": question}]
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.4,
            max_tokens=1200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


def generate_quiz(max_q: int, difficulty: str, context: str) -> List[Dict]:
    if not client:
        raise ValueError("API client not initialized.")
    if not context.strip():
        raise ValueError("No content available for quiz generation.")
    prompt = f"""Generate exactly {max_q} multiple-choice questions based on:

{context[:8000]}

RULES:
- Return ONLY a valid JSON array
- Each object: {{"question": "...", "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}}, "correct": "A"}}
- "correct" must be exactly "A", "B", "C", or "D"
- Questions should be at {difficulty} level
- Include a brief "explanation" field for each answer
- No markdown formatting, no extra text"""
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a precise quiz generator. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2500
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()
        start, end = raw.find("["), raw.rfind("]")
        if start == -1 or end == -1:
            raise ValueError("No JSON array found in response.")
        quiz_data = json.loads(raw[start:end+1])
        if not isinstance(quiz_data, list):
            raise ValueError("Response is not a JSON array.")
        normalized = []
        for i, q in enumerate(quiz_data):
            if not isinstance(q, dict):
                continue
            options = {}
            raw_opts = q.get("options", {})
            if isinstance(raw_opts, dict):
                options = {k.upper(): str(v) for k, v in raw_opts.items() if k.upper() in "ABCD"}
            elif isinstance(raw_opts, list) and len(raw_opts) >= 4:
                options = {chr(65+j): str(raw_opts[j]) for j in range(4)}
            for key in "ABCD":
                if key not in options:
                    options[key] = "N/A"
            correct = str(q.get("correct") or q.get("answer") or "A").strip().upper()
            if correct not in options:
                correct_text = str(q.get("correct") or "").strip()
                for k, v in options.items():
                    if correct_text.lower() == v.lower():
                        correct = k
                        break
                else:
                    correct = "A"
            normalized.append({
                "question": q.get("question", f"Question {i+1}"),
                "options": options,
                "correct": correct,
                "explanation": q.get("explanation", "No explanation provided.")
            })
        return normalized
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from API: {e}")
    except Exception as e:
        raise ValueError(f"Quiz generation failed: {e}")


# =========================================================
# API INTEGRATIONS
# =========================================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_word_meaning(word: str) -> str:
    if not word or not word.strip():
        return "Please enter a valid word."
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.strip().lower()}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        meanings = []
        for meaning in data[0].get("meanings", [])[:2]:
            pos = meaning.get("partOfSpeech", "")
            defs = [d.get("definition", "") for d in meaning.get("definitions", [])[:2]]
            meanings.append(f"**{pos}:** " + "; ".join(defs))
        return "\n\n".join(meanings) if meanings else "No definitions found."
    except Exception:
        return "Unable to fetch definition."


@st.cache_data(ttl=600, show_spinner=False)
def get_weather(lat: float = 23.25, lon: float = 87.85) -> str:
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        temp = data["current_weather"]["temperature"]
        wind = data["current_weather"]["windspeed"]
        code = data["current_weather"].get("weathercode", 0)
        weather_emojis = {0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 51: "🌦️", 61: "🌧️", 71: "❄️", 95: "⛈️"}
        emoji = weather_emojis.get(code, "🌡️")
        return f"{emoji} **{temp}°C** | 💨 {wind} km/h"
    except Exception:
        return "🌡️ Weather unavailable"


@st.cache_data(ttl=1800, show_spinner=False)
def search_arxiv(query: str) -> List[Tuple[str, str]]:
    if not query or not query.strip():
        return []
    try:
        encoded = requests.utils.quote(query.strip())
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded}&start=0&max_results=5"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        results = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            link = entry.find("atom:id", ns)
            if title is not None and link is not None:
                results.append((title.text.strip(), link.text.strip()))
        return results
    except Exception:
        return []


# =========================================================
# UI COMPONENTS
# =========================================================
def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
            <div style='border-left: 4px solid #34d399; background: linear-gradient(90deg, rgba(52,211,153,0.08) 0%, transparent 100%); padding: 1.25rem 1.5rem; border-radius: 0 14px 14px 0; margin-bottom: 0.5rem;'>
                <h1 style='margin: 0; color: #f1f5f9; font-size: 2.2rem; letter-spacing: -0.02em; font-weight: 800;'>🎓 Elevate AI Tutor</h1>
                <p style='color: #94a3b8; font-size: 1rem; margin: 0.25rem 0 0 0;'>Intelligent Learning Platform • AI-Powered • Data-Driven</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.session_state.last_activity:
            st.markdown(f"""
                <div style='text-align: right; color: #475569; font-size: 0.875rem;'>
                    <span style='color: #34d399;'>●</span> Last Active<br>
                    <b style='color: #94a3b8;'>{st.session_state.last_activity}</b>
                </div>
            """, unsafe_allow_html=True)


def render_analytics_dashboard():
    """Render analytics using native Streamlit metrics (works reliably in sidebar)."""
    analytics = st.session_state.analytics
    total_q = analytics["total_questions"]
    total_s = analytics["total_score"]
    avg = round((total_s / total_q) * 100, 1) if total_q > 0 else 0
    
    st.markdown("### 📊 Analytics")
    
    # Use native st.metric which works properly in sidebar
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="Quizzes", value=analytics['quizzes_taken'])
    with c2:
        st.metric(label="Avg Score", value=f"{avg}%")
    
    # Additional stats in a cleaner format
    if analytics['quizzes_taken'] > 0:
        st.caption(f"Total questions answered: **{total_q}** | Correct: **{total_s}**")
    else:
        st.caption("Complete a quiz to see your stats")


def export_quiz_results():
    if not st.session_state.quiz_questions or st.session_state.quiz_score is None:
        return
    quiz_data = st.session_state.quiz_questions
    answers = st.session_state.answers
    export_data = []
    for idx, q in enumerate(quiz_data):
        user_ans = answers.get(idx, "—")
        correct = q["correct"]
        is_correct = str(user_ans).strip().upper() == str(correct).strip().upper()
        export_data.append({
            "Question #": idx + 1,
            "Question": q["question"],
            "Your Answer": f"{user_ans}: {q['options'].get(user_ans, 'N/A')}",
            "Correct Answer": f"{correct}: {q['options'][correct]}",
            "Result": "Correct" if is_correct else "Incorrect",
            "Explanation": q.get("explanation", "")
        })
    df = pd.DataFrame(export_data)
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False)
        st.download_button("📥 CSV Report", csv, f"quiz_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv", use_container_width=True)
    with col2:
        json_str = json.dumps(export_data, indent=2)
        st.download_button("📥 JSON Report", json_str, f"quiz_results_{datetime.now().strftime('%Y%m%d_%H%M')}.json", "application/json", use_container_width=True)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding-bottom: 1.5rem; border-bottom: 1px solid rgba(148, 163, 184, 0.1); margin-bottom: 1.5rem;'>
            <h2 style='color: #f1f5f9 !important; margin: 0; font-size: 1.5rem;'>⚙️ Control Center</h2>
            <p style='color: #475569; font-size: 0.8rem; margin-top: 0.5rem;'>Configure your session</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not OPENROUTER_API_KEY:
        st.warning("🔑 API Key Required", icon="⚠️")
    
    difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"], index=1)
    
    # Quiz Intensity with emerald border effect
    st.markdown("""
        <div style='border-left: 3px solid #34d399; background: linear-gradient(90deg, rgba(52,211,153,0.06) 0%, transparent 100%); padding: 0.75rem 1rem; border-radius: 0 10px 10px 0; margin: 1rem 0 0.5rem 0;'>
            <div style='color: #94a3b8; font-size: 0.875rem; font-weight: 500;'>Quiz Intensity</div>
        </div>
    """, unsafe_allow_html=True)
    max_questions = st.slider("", 3, 15, 5, key="quiz_intensity_slider")
    st.caption(f"Selected: **{max_questions}** questions")
    
    st.divider()
    render_analytics_dashboard()
    
    st.divider()
    st.markdown("### 🌤️ Environment")
    if st.button("Check Weather", key="btn_weather", use_container_width=True):
        st.info(get_weather())
    
    st.divider()
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History", key="btn_clear", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    st.markdown("""
        <div style='text-align: center; margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid rgba(148, 163, 184, 0.1); color: #475569; font-size: 0.75rem;'>
            <p style='margin: 0; color: #64748b;'>Elevate AI Tutor v2.0</p>
            <p style='margin: 0.25rem 0 0 0; color: #475569;'>Built with Streamlit</p>
        </div>
    """, unsafe_allow_html=True)


# =========================================================
# MAIN TABS
# =========================================================
render_header()
st.markdown("<hr style='margin: 1.5rem 0; border-color: rgba(148, 163, 184, 0.1);'>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📖 Upload & Analyze", "💬 AI Tutor", "🧠 Smart Quiz"])

# -------------------------
# TAB 1: Upload & Analyze
# -------------------------
with tab1:
    st.markdown("### Upload Study Material")
    
    file = st.file_uploader(
        "Drop your file here — TXT, PDF, or HTML",
        type=["txt", "pdf", "html", "htm"],
        key="file_uploader",
        help="Upload study material to begin AI analysis"
    )
    
    if file:
        with st.spinner("Processing document..."):
            extracted = extract_text(file)
        
        if extracted:
            st.session_state.text_content = extracted
            st.session_state.last_activity = datetime.now().strftime("%H:%M")
            st.success("✅ Document processed successfully!")
            
            stats = calculate_content_stats(extracted)
            
            st.markdown("#### 📈 Content Intelligence")
            c1, c2, c3, c4, c5 = st.columns(5)
            metrics = [
                (c1, "Words", stats["words"], "#34d399"),
                (c2, "Sentences", stats["sentences"], "#818cf8"),
                (c3, "Paragraphs", stats["paragraphs"], "#c084fc"),
                (c4, "Avg Length", stats["avg_word_length"], "#fbbf24"),
                (c5, "Read Time", stats["reading_time"], "#2dd4bf")
            ]
            for col, label, value, color in metrics:
                with col:
                    st.markdown(f"""
                        <div class='glass-card' style='text-align: center; border-top: 2px solid {color};'>
                            <div style='font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;'>{label}</div>
                            <div style='font-size: 1.5rem; font-weight: 800; color: {color};'>{value}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            if client and st.button("✨ Generate AI Summary", use_container_width=False):
                with st.spinner("Analyzing with AI..."):
                    summary = generate_summary(extracted)
                st.session_state.text_summary = summary
                st.rerun()
            
            if st.session_state.text_summary:
                with st.expander("📝 AI-Generated Summary", expanded=True):
                    st.markdown(st.session_state.text_summary)
            
            with st.expander("📄 Document Preview", expanded=False):
                preview = extracted[:3000] + ("..." if len(extracted) > 3000 else "")
                st.text_area("Preview", preview, height=400, disabled=True, label_visibility="collapsed")
        else:
            st.error("❌ Could not extract text from the uploaded file.")

# -------------------------
# TAB 2: AI Tutor
# -------------------------
with tab2:
    if not st.session_state.text_content:
        st.info("👆 Upload study material in the **Upload & Analyze** tab to activate the AI Tutor.")
    else:
        st.markdown("### 💬 Intelligent Tutoring Session")
        
        if st.session_state.chat_history:
            with st.container():
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f"<div class='chat-user'><b style='color: #34d399;'>🧑‍🎓 You</b><br>{msg['content']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='chat-assistant'><b style='color: #34d399;'>🤖 Tutor</b><br>{msg['content']}</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 2rem;'>", unsafe_allow_html=True)
        question = st.text_area(
            "Ask your question:",
            height=100,
            key="doubt_input",
            placeholder="e.g., Explain the core concept and give me a real-world example..."
        )
        
        btn_col1, btn_col2 = st.columns([1, 5])
        with btn_col1:
            ask_clicked = st.button("🚀 Ask", key="btn_ask", use_container_width=True)
        with btn_col2:
            if st.session_state.chat_history:
                st.caption(f"{len(st.session_state.chat_history)//2} exchanges in this session")
        
        if ask_clicked:
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Thinking..."):
                    answer = generate_explanation(question, difficulty, st.session_state.text_content)
                if not answer.startswith("⚠️") and not answer.startswith("Error"):
                    st.session_state.chat_history.append({"role": "user", "content": question})
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    st.session_state.last_activity = datetime.now().strftime("%H:%M")
                    st.rerun()
                else:
                    st.error(answer)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.divider()
        
        tool_col1, tool_col2 = st.columns(2)
        with tool_col1:
            st.markdown("#### 📖 Dictionary")
            word = st.text_input("Look up a word:", key="dict_input", placeholder="e.g., photosynthesis")
            if st.button("🔍 Define", key="btn_dict"):
                if word.strip():
                    with st.spinner("Searching..."):
                        meaning = get_word_meaning(word)
                    st.info(f"**{word.strip().capitalize()}**\n\n{meaning}")
                else:
                    st.warning("Enter a word to search.")
        
        with tool_col2:
            st.markdown("#### 🔬 arXiv Research")
            query = st.text_input("Search papers:", key="arxiv_input", placeholder="e.g., transformer architectures")
            if st.button("🔍 Search", key="btn_arxiv"):
                if query.strip():
                    with st.spinner("Searching arXiv..."):
                        papers = search_arxiv(query)
                    if papers:
                        st.success(f"Found {len(papers)} papers")
                        for title, link in papers:
                            st.markdown(f"- [{title}]({link})")
                    else:
                        st.warning("No papers found.")
                else:
                    st.warning("Enter a search term.")

# -------------------------
# TAB 3: Smart Quiz
# -------------------------
with tab3:
    st.markdown("""
        <div style='border-left: 4px solid #34d399; background: linear-gradient(90deg, rgba(52,211,153,0.08) 0%, transparent 100%); padding: 1rem 1.25rem; border-radius: 0 12px 12px 0; margin-bottom: 1rem;'>
            <h3 style='margin: 0; color: #f1f5f9; font-size: 1.5rem; font-weight: 700;'>🧠 Adaptive Assessment</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.text_content:
        st.info("👆 Upload content in the **Upload & Analyze** tab to generate a quiz.")
    elif not client:
        st.error("🔑 Configure your OpenRouter API key in the sidebar to use the quiz feature.")
    else:
        gen_col1, gen_col2 = st.columns([1, 3])
        with gen_col1:
            if st.button("🎲 Generate New Quiz", key="btn_gen_quiz", use_container_width=True):
                try:
                    with st.spinner("Crafting questions with AI..."):
                        quiz = generate_quiz(max_questions, difficulty, st.session_state.text_content)
                    clear_quiz_keys()
                    st.session_state.quiz_questions = quiz
                    st.session_state.answers = {}
                    st.session_state.quiz_score = None
                    st.session_state.quiz_submitted = False
                    st.session_state.last_activity = datetime.now().strftime("%H:%M")
                    st.success("✅ Quiz generated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)}")
        
        with gen_col2:
            if st.session_state.quiz_questions:
                st.caption(f"Current: {len(st.session_state.quiz_questions)} questions • {difficulty} level")
        
        if st.session_state.quiz_questions:
            quiz_data = st.session_state.quiz_questions
            
            # RESULTS VIEW
            if st.session_state.quiz_submitted and st.session_state.quiz_score is not None:
                score = st.session_state.quiz_score
                total = len(quiz_data)
                percentage = round((score / total) * 100, 1) if total > 0 else 0
                
                st.session_state.analytics["quizzes_taken"] += 1
                st.session_state.analytics["total_score"] += score
                st.session_state.analytics["total_questions"] += total
                
                score_color = "#34d399" if percentage >= 70 else "#fbbf24" if percentage >= 50 else "#f87171"
                
                st.markdown(f"""
                    <div class='glass-card' style='text-align: center; padding: 2.5rem; border: 1px solid rgba(52, 211, 153, 0.2);'>
                        <div style='font-size: 0.875rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;'>Performance Score</div>
                        <div style='font-size: 4rem; font-weight: 800; color: {score_color}; text-shadow: 0 0 30px {score_color}40;'>
                            {percentage}%
                        </div>
                        <div style='font-size: 1.1rem; color: #94a3b8; margin-top: 0.75rem;'>
                            {score} / {total} correct answers
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.progress(score / total if total > 0 else 0)
                
                if percentage >= 80:
                    st.success("🏆 Outstanding! You've mastered this material.")
                elif percentage >= 60:
                    st.info("👍 Good work. Review the explanations below to close gaps.")
                else:
                    st.warning("📚 Keep practicing. Focus areas identified below.")
                
                st.markdown("#### 📥 Export Results")
                export_quiz_results()
                
                st.markdown("#### 📊 Answer Breakdown")
                for idx, q in enumerate(quiz_data):
                    user_ans = st.session_state.answers.get(idx, "—")
                    correct_ans = q["correct"]
                    is_correct = str(user_ans).strip().upper() == str(correct_ans).strip().upper()
                    
                    with st.expander(f"{'✅' if is_correct else '❌'} Q{idx+1}: {q['question'][:50]}...", expanded=not is_correct):
                        st.write(q["question"])
                        st.markdown(f"**Your Answer:** `{user_ans}` — {q['options'].get(user_ans, 'N/A')}")
                        st.markdown(f"**Correct Answer:** `{correct_ans}` — {q['options'][correct_ans]}")
                        if not is_correct:
                            st.info(f"💡 **Why:** {q.get('explanation', 'Review this concept in the source material.')}")
                
                if st.button("🔄 Start New Quiz", key="btn_restart", use_container_width=True):
                    clear_quiz_keys()
                    st.session_state.quiz_questions = []
                    st.session_state.answers = {}
                    st.session_state.quiz_score = None
                    st.session_state.quiz_submitted = False
                    st.rerun()
            
            # QUIZ TAKING VIEW
            else:
                st.markdown(f"**Answer all {len(quiz_data)} questions**")
                st.caption("Select the best answer for each. All questions must be answered before submitting.")
                
                for idx, q in enumerate(quiz_data):
                    st.markdown(f"**Question {idx+1} of {len(quiz_data)}**")
                    st.write(q["question"])
                    
                    options = list(q["options"].keys())
                    selected = st.radio(
                        "Select your answer:",
                        options=options,
                        format_func=lambda x: f"{x}: {q['options'][x]}",
                        key=f"question_{idx}",
                        index=None,
                        label_visibility="collapsed"
                    )
                    
                    if selected:
                        st.session_state.answers[idx] = selected
                    
                    st.divider()
                
                answered_count = len(st.session_state.answers)
                total_q = len(quiz_data)
                
                st.progress(answered_count / total_q if total_q > 0 else 0)
                st.caption(f"Progress: {answered_count}/{total_q} answered")
                
                if answered_count < total_q:
                    missing = [str(i+1) for i in range(total_q) if i not in st.session_state.answers]
                    st.warning(f"⚠️ Please answer: {', '.join(missing)}")
                
                if st.button("✅ Submit Quiz", key="btn_submit", use_container_width=True):
                    if answered_count < total_q:
                        st.error("Answer all questions before submitting.")
                    else:
                        score = 0
                        for idx, q in enumerate(quiz_data):
                            user = str(st.session_state.answers.get(idx, "")).strip().upper()
                            correct = str(q["correct"]).strip().upper()
                            if user == correct:
                                score += 1
                        st.session_state.quiz_score = score
                        st.session_state.quiz_submitted = True
                        st.rerun()


# =========================================================
# FOOTER
# =========================================================
st.markdown("""
    <div class='footer'>
        <p style='color: #475569; margin-bottom: 0.5rem;'>🎓 <b style='color: #94a3b8;'>Elevate AI Tutor</b> • Built for Modern Learning</p>
        <p style='color: #334155; font-size: 0.75rem; margin: 0;'>AI Tutoring • Adaptive Quizzing • Content Analytics • arXiv Integration</p>
    </div>
""", unsafe_allow_html=True)