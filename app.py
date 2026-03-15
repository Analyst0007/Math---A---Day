import streamlit as st
import tempfile
import os
import json
import base64
import asyncio
from groq import Groq
import edge_tts

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MathMagic — AI Math Tutor",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Fredoka+One&display=swap');

:root {
    --sky: #e8f4fd;
    --blue: #3b82f6;
    --blue-dark: #1d4ed8;
    --yellow: #fbbf24;
    --yellow-light: #fef3c7;
    --green: #10b981;
    --green-light: #d1fae5;
    --pink: #ec4899;
    --pink-light: #fce7f3;
    --orange: #f97316;
    --orange-light: #ffedd5;
    --purple: #8b5cf6;
    --purple-light: #ede9fe;
    --red: #ef4444;
    --white: #ffffff;
    --ink: #1e293b;
    --muted: #64748b;
    --border: #e2e8f0;
}

html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e0f2fe 0%, #f0fdf4 50%, #fef9c3 100%) !important;
    font-family: 'Nunito', sans-serif !important;
    color: var(--ink);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3a5f 0%, #1e1b4b 100%) !important;
    border-right: 3px solid var(--yellow) !important;
}

[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--yellow) !important;
    font-family: 'Fredoka One', cursive !important;
}
[data-testid="stSidebar"] label {
    color: #94a3b8 !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

.hero {
    text-align: center;
    padding: 2rem 0 1rem;
}
.hero h1 {
    font-family: 'Fredoka One', cursive;
    font-size: 3.5rem;
    background: linear-gradient(135deg, var(--blue) 0%, var(--purple) 50%, var(--pink) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
}
.hero p {
    color: var(--muted);
    font-size: 1.05rem;
    font-weight: 600;
    margin-top: 0.4rem;
}

.mode-card {
    background: white;
    border-radius: 20px;
    padding: 1.2rem 1rem;
    text-align: center;
    border: 3px solid transparent;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}
.mode-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
.mode-card .icon { font-size: 2.2rem; }
.mode-card .label {
    font-family: 'Fredoka One', cursive;
    font-size: 1rem;
    margin-top: 0.3rem;
    color: var(--ink);
}

.chat-user {
    background: linear-gradient(135deg, var(--blue) 0%, var(--blue-dark) 100%);
    color: white;
    border-radius: 20px 20px 5px 20px;
    padding: 1rem 1.25rem;
    margin: 0.6rem 0;
    max-width: 78%;
    margin-left: auto;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 4px 12px rgba(59,130,246,0.3);
    font-weight: 600;
}

.chat-ai {
    background: white;
    color: var(--ink);
    border-radius: 20px 20px 20px 5px;
    padding: 1rem 1.25rem;
    margin: 0.6rem 0;
    max-width: 85%;
    font-size: 0.95rem;
    line-height: 1.7;
    border: 2px solid var(--border);
    box-shadow: 0 4px 15px rgba(0,0,0,0.06);
}

.step-box {
    background: linear-gradient(135deg, var(--purple-light) 0%, white 100%);
    border: 2px solid var(--purple);
    border-radius: 16px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0 1rem;
}
.step-box .step-title {
    font-family: 'Fredoka One', cursive;
    color: var(--purple);
    font-size: 0.9rem;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

.quiz-card {
    background: white;
    border: 3px solid var(--yellow);
    border-radius: 20px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(251,191,36,0.2);
}
.quiz-card .q-num {
    font-family: 'Fredoka One', cursive;
    color: var(--orange);
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.quiz-card .q-text {
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0.3rem 0 0.8rem;
    color: var(--ink);
}

.concept-card {
    background: linear-gradient(135deg, var(--green-light) 0%, white 100%);
    border: 2px solid var(--green);
    border-radius: 20px;
    padding: 1.25rem;
    margin: 0.5rem 0;
}
.concept-card .c-title {
    font-family: 'Fredoka One', cursive;
    color: var(--green);
    font-size: 1rem;
    margin-bottom: 0.5rem;
}

.badge {
    display: inline-block;
    border-radius: 999px;
    padding: 0.2rem 0.75rem;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.badge-blue { background: #dbeafe; color: var(--blue-dark); }
.badge-green { background: var(--green-light); color: #065f46; }
.badge-yellow { background: var(--yellow-light); color: #92400e; }
.badge-pink { background: var(--pink-light); color: #9d174d; }
.badge-orange { background: var(--orange-light); color: #9a3412; }

.fun-divider {
    text-align: center;
    font-size: 1.5rem;
    margin: 1rem 0;
    letter-spacing: 0.5rem;
    opacity: 0.4;
}

.stButton > button {
    background: linear-gradient(135deg, var(--blue) 0%, var(--purple) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.4) !important;
}

.empty-hero {
    text-align: center;
    padding: 2.5rem 1rem;
    background: white;
    border-radius: 24px;
    border: 3px dashed var(--border);
    margin: 1rem 0;
}
.empty-hero .big-icon { font-size: 4rem; margin-bottom: 0.5rem; }
.empty-hero p { color: var(--muted); font-size: 0.95rem; font-weight: 600; }

.lang-toggle {
    background: var(--yellow-light);
    border: 2px solid var(--yellow);
    border-radius: 12px;
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    font-weight: 700;
    color: #92400e;
    text-align: center;
    margin-bottom: 0.5rem;
}

.stTextArea textarea {
    border-radius: 14px !important;
    border: 2px solid var(--border) !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.95rem !important;
}
.stTextArea textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}

[data-testid="stAudioInput"] {
    border: 3px dashed var(--blue) !important;
    border-radius: 16px !important;
    background: var(--sky) !important;
}

.grade-pill {
    display: inline-block;
    background: linear-gradient(135deg, var(--orange) 0%, var(--pink) 100%);
    color: white;
    border-radius: 999px;
    padding: 0.25rem 1rem;
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State ───────────────────────────────────────────────────────────
for key, default in {
    "messages": [],
    "mode": "solver",
    "quiz_questions": [],
    "quiz_answers": {},
    "quiz_checked": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧮 MathMagic")
    st.markdown("*Your AI Math Tutor*")
    st.markdown("---")

    groq_api_key = st.text_input("🔑 Groq API Key", type="password",
                                  help="Free at console.groq.com")

    st.markdown("---")
    st.markdown("### 🎓 Your Grade")
    grade = st.selectbox("Select Grade", [f"Grade {i}" for i in range(1, 13)], index=6)

    st.markdown("---")
    st.markdown("### 🌐 Language")
    language = st.selectbox("Explain in", [
        "English",
        "Hindi (हिंदी)",
        "Gujarati (ગુજરાતી)",
        "English + Hindi",
        "English + Gujarati",
    ])

    st.markdown("---")
    st.markdown("### 🎯 Mode")
    mode_options = {
        "🔍 Problem Solver": "solver",
        "📖 Concept Explainer": "concept",
        "📝 Practice Quiz": "quiz",
    }
    selected_mode_label = st.radio("Choose mode", list(mode_options.keys()))
    st.session_state.mode = mode_options[selected_mode_label]

    st.markdown("---")
    st.markdown("### ⚡ Voice Reply")
    voice_reply = st.toggle("Read answer aloud", value=False)
    voice_choice = st.selectbox("Voice", ["en-US-JennyNeural", "en-US-GuyNeural", "en-GB-SoniaNeural"])

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.quiz_questions = []
        st.session_state.quiz_answers = {}
        st.session_state.quiz_checked = False
        st.rerun()

# ─── Helper Functions ─────────────────────────────────────────────────────────

def get_client():
    key = groq_api_key or os.environ.get("GROQ_API_KEY", "")
    return Groq(api_key=key) if key else None

def transcribe_audio(client, audio_bytes):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        tmp = f.name
    try:
        with open(tmp, "rb") as af:
            result = client.audio.transcriptions.create(
                model="whisper-large-v3", file=af, language="en")
        return result.text
    finally:
        os.unlink(tmp)

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")

GRADE_CONTEXT = {
    **{f"Grade {i}": f"elementary school Grade {i} student (age {i+5})" for i in range(1, 6)},
    **{f"Grade {i}": f"middle school Grade {i} student (age {i+5})" for i in range(6, 9)},
    **{f"Grade {i}": f"high school Grade {i} student (age {i+5})" for i in range(9, 13)},
}

LANG_INSTRUCTION = {
    "English": "Respond entirely in English.",
    "Hindi (हिंदी)": "Respond entirely in Hindi (हिंदी में जवाब दें).",
    "Gujarati (ગુજરાતી)": "Respond entirely in Gujarati (ગુજરાતીમાં જવાબ આપો).",
    "English + Hindi": "Respond in both English and Hindi. First give the full answer in English, then repeat key points in Hindi.",
    "English + Gujarati": "Respond in both English and Gujarati. First give the full answer in English, then repeat key points in Gujarati.",
}

def build_solver_prompt(grade, language):
    grade_ctx = GRADE_CONTEXT.get(grade, "student")
    lang_instr = LANG_INSTRUCTION.get(language, "Respond in English.")
    return f"""You are MathMagic, a super friendly and encouraging AI math tutor for a {grade_ctx}.

{lang_instr}

PERSONALITY: Warm, encouraging, uses simple language, celebrates the student's effort. Use emojis occasionally to keep it fun.

WHEN SOLVING A PROBLEM, always respond with this JSON format:
{{
  "reply": "A warm, friendly intro (1 sentence, acknowledge the problem).",
  "steps": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "answer": "The final answer clearly stated.",
  "tip": "One helpful tip or fun fact related to this topic.",
  "encouragement": "A short encouraging message for the student."
}}

- Use simple language appropriate for {grade}
- Break every solution into CLEAR numbered steps
- Never just give the answer — always show the working
- If the problem has a diagram or visual in a photo, describe what you see and solve it"""

def build_concept_prompt(grade, language):
    grade_ctx = GRADE_CONTEXT.get(grade, "student")
    lang_instr = LANG_INSTRUCTION.get(language, "Respond in English.")
    return f"""You are MathMagic, a super friendly math teacher explaining concepts to a {grade_ctx}.

{lang_instr}

PERSONALITY: Use simple analogies, real-life examples, and fun comparisons. Make math feel exciting!

Respond in this JSON format:
{{
  "reply": "Enthusiastic intro to the concept.",
  "explanation": "Clear explanation using simple language and a real-life analogy.",
  "example": "A worked example appropriate for {grade}.",
  "remember": "One key thing to always remember about this concept.",
  "fun_fact": "An interesting or surprising fact related to this concept."
}}"""

def build_quiz_prompt(grade, topic, language):
    grade_ctx = GRADE_CONTEXT.get(grade, "student")
    lang_instr = LANG_INSTRUCTION.get(language, "Respond in English.")
    return f"""Generate a practice quiz for a {grade_ctx} on the topic: {topic}.
{lang_instr}

Return ONLY valid JSON — no extra text:
{{
  "topic": "{topic}",
  "questions": [
    {{
      "question": "Question text here",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "A",
      "explanation": "Why this is correct"
    }}
  ]
}}

Generate exactly 5 questions. Make them appropriate for {grade}. Mix easy, medium and slightly challenging questions."""

def call_llm(client, system_prompt, user_message, image_b64=None):
    content = []
    if image_b64:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}})
    content.append({"type": "text", "text": user_message})

    history = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages[-8:]:  # last 8 for context
        history.append({"role": msg["role"], "content": msg["content"]})
    history.append({"role": "user", "content": content if image_b64 else user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=history,
        temperature=0.5,
        max_tokens=1200,
    )
    return response.choices[0].message.content.strip()

def parse_json_response(raw):
    try:
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception:
        return None

async def tts_async(text, voice):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp = f.name
    await edge_tts.Communicate(text, voice).save(tmp)
    with open(tmp, "rb") as f:
        data = f.read()
    os.unlink(tmp)
    return data

def speak(text, voice):
    try:
        audio = asyncio.run(tts_async(text, voice))
        b64 = base64.b64encode(audio).decode()
        st.markdown(f'<audio autoplay style="display:none"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except Exception:
        pass

# ─── Main UI ──────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <h1>🧮 MathMagic</h1>
    <p>Your friendly AI Math Tutor for Grade 1 to 12 ✨</p>
</div>
""", unsafe_allow_html=True)

# Grade + mode badges
col_b1, col_b2, col_b3 = st.columns([1,1,1])
with col_b1:
    st.markdown(f'<div style="text-align:center"><span class="grade-pill">🎓 {grade}</span></div>', unsafe_allow_html=True)
with col_b2:
    mode_labels = {"solver": "🔍 Problem Solver", "concept": "📖 Concept Explainer", "quiz": "📝 Practice Quiz"}
    st.markdown(f'<div style="text-align:center"><span class="badge badge-blue">{mode_labels[st.session_state.mode]}</span></div>', unsafe_allow_html=True)
with col_b3:
    st.markdown(f'<div style="text-align:center"><span class="badge badge-green">🌐 {language.split(" ")[0]}</span></div>', unsafe_allow_html=True)

st.markdown('<div class="fun-divider">⭐ ➕ ✖️ ➗ ⭐</div>', unsafe_allow_html=True)

# ─── API Key Check ────────────────────────────────────────────────────────────
if not groq_api_key and not os.environ.get("GROQ_API_KEY"):
    st.warning("⚠️ Please enter your **Groq API Key** in the sidebar to start! Get one free at [console.groq.com](https://console.groq.com)")
    st.stop()

client = get_client()

# ══════════════════════════════════════════════════════════════════════════════
# MODE: PRACTICE QUIZ
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.mode == "quiz":
    st.markdown("### 📝 Practice Quiz Generator")

    quiz_col1, quiz_col2 = st.columns([3, 1])
    with quiz_col1:
        quiz_topic = st.text_input("📚 Enter a math topic for your quiz",
                                    placeholder="e.g. Fractions, Quadratic Equations, Trigonometry...")
    with quiz_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        gen_quiz = st.button("🎲 Generate Quiz!", use_container_width=True)

    if gen_quiz and quiz_topic:
        with st.spinner("🎯 Creating your quiz..."):
            try:
                system_prompt = build_quiz_prompt(grade, quiz_topic, language)
                raw = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Return ONLY valid JSON, no markdown, no extra text."},
                        {"role": "user", "content": system_prompt}
                    ],
                    temperature=0.6,
                    max_tokens=1500,
                ).choices[0].message.content.strip()

                data = parse_json_response(raw)
                if data and "questions" in data:
                    st.session_state.quiz_questions = data["questions"]
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_checked = False
                else:
                    st.error("Could not generate quiz. Try a different topic.")
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.quiz_questions:
        st.markdown(f"#### 🎯 Quiz: {quiz_topic if 'quiz_topic' in dir() else 'Math'}")
        for i, q in enumerate(st.session_state.quiz_questions):
            st.markdown(f"""
            <div class="quiz-card">
                <div class="q-num">Question {i+1} of {len(st.session_state.quiz_questions)}</div>
                <div class="q-text">{q['question']}</div>
            </div>
            """, unsafe_allow_html=True)

            ans = st.radio(f"Your answer for Q{i+1}:",
                           q.get("options", ["A", "B", "C", "D"]),
                           key=f"quiz_{i}", index=None)
            if ans:
                letter = ans[0]
                st.session_state.quiz_answers[i] = letter

        if len(st.session_state.quiz_answers) == len(st.session_state.quiz_questions):
            if st.button("✅ Check My Answers!", use_container_width=True):
                st.session_state.quiz_checked = True

        if st.session_state.quiz_checked:
            score = 0
            st.markdown("### 📊 Results")
            for i, q in enumerate(st.session_state.quiz_questions):
                user_ans = st.session_state.quiz_answers.get(i, "?")
                correct = q.get("answer", "A")[0]
                is_correct = user_ans == correct
                if is_correct:
                    score += 1
                icon = "✅" if is_correct else "❌"
                color = "green" if is_correct else "red"
                st.markdown(f"""
                <div style="background:{'#d1fae5' if is_correct else '#fee2e2'};
                     border-radius:12px; padding:0.75rem 1rem; margin:0.4rem 0;
                     border-left:4px solid {'var(--green)' if is_correct else 'var(--red)'}">
                    <strong>{icon} Q{i+1}:</strong> Your answer: <strong>{user_ans}</strong> |
                    Correct: <strong>{correct}</strong><br>
                    <small>💡 {q.get('explanation','')}</small>
                </div>
                """, unsafe_allow_html=True)

            pct = int(score / len(st.session_state.quiz_questions) * 100)
            emoji = "🏆" if pct >= 80 else "👍" if pct >= 50 else "💪"
            msg = "Excellent work!" if pct >= 80 else "Good effort, keep practicing!" if pct >= 50 else "Don't give up, try again!"
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#dbeafe,#ede9fe);
                 border-radius:20px; padding:1.5rem; text-align:center; margin:1rem 0;
                 border:3px solid var(--blue)">
                <div style="font-family:'Fredoka One',cursive; font-size:2rem; color:var(--blue-dark)">
                    {emoji} {score}/{len(st.session_state.quiz_questions)} — {pct}%
                </div>
                <div style="font-weight:700; color:var(--ink); margin-top:0.3rem">{msg}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MODE: SOLVER & CONCEPT EXPLAINER
# ══════════════════════════════════════════════════════════════════════════════
else:
    # Chat history
    if not st.session_state.messages:
        mode_hints = {
            "solver": ("🔍", "Problem Solver", "Type, speak, or photo a math problem and I'll solve it step by step!"),
            "concept": ("📖", "Concept Explainer", "Ask me to explain any math concept — fractions, algebra, calculus and more!"),
        }
        icon, title, desc = mode_hints[st.session_state.mode]
        st.markdown(f"""
        <div class="empty-hero">
            <div class="big-icon">{icon}</div>
            <div style="font-family:'Fredoka One',cursive;font-size:1.4rem;color:var(--ink)">{title} Ready!</div>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">🧑‍🎓 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                data = msg.get("parsed")
                if data and st.session_state.mode == "solver":
                    st.markdown(f'<div class="chat-ai">🤖 {data.get("reply","")}</div>', unsafe_allow_html=True)
                    if data.get("steps"):
                        steps_html = "".join([f"<div style='margin:0.3rem 0'>{'  ' if not s.startswith('Step') else ''}{s}</div>" for s in data["steps"]])
                        st.markdown(f"""
                        <div class="step-box">
                            <div class="step-title">📐 Step-by-Step Solution</div>
                            {steps_html}
                        </div>
                        """, unsafe_allow_html=True)
                    if data.get("answer"):
                        st.markdown(f"""
                        <div style="background:linear-gradient(135deg,var(--green-light),white);
                             border:2px solid var(--green);border-radius:14px;
                             padding:0.75rem 1.25rem;margin:0.3rem 0">
                            <strong>✅ Answer:</strong> {data['answer']}
                        </div>""", unsafe_allow_html=True)
                    if data.get("tip"):
                        st.markdown(f"""
                        <div style="background:var(--yellow-light);border:2px solid var(--yellow);
                             border-radius:14px;padding:0.6rem 1rem;margin:0.3rem 0;font-size:0.88rem">
                            💡 <strong>Tip:</strong> {data['tip']}
                        </div>""", unsafe_allow_html=True)
                    if data.get("encouragement"):
                        st.markdown(f"""
                        <div style="text-align:center;padding:0.5rem;font-weight:700;
                             color:var(--pink);font-size:0.9rem">
                            🌟 {data['encouragement']}
                        </div>""", unsafe_allow_html=True)

                elif data and st.session_state.mode == "concept":
                    st.markdown(f'<div class="chat-ai">🤖 {data.get("reply","")}</div>', unsafe_allow_html=True)
                    if data.get("explanation"):
                        st.markdown(f"""
                        <div class="concept-card">
                            <div class="c-title">📖 Explanation</div>
                            {data['explanation']}
                        </div>""", unsafe_allow_html=True)
                    if data.get("example"):
                        st.markdown(f"""
                        <div class="step-box">
                            <div class="step-title">✏️ Worked Example</div>
                            {data['example']}
                        </div>""", unsafe_allow_html=True)
                    if data.get("remember"):
                        st.markdown(f"""
                        <div style="background:var(--pink-light);border:2px solid var(--pink);
                             border-radius:14px;padding:0.6rem 1rem;margin:0.3rem 0">
                            🧠 <strong>Remember:</strong> {data['remember']}
                        </div>""", unsafe_allow_html=True)
                    if data.get("fun_fact"):
                        st.markdown(f"""
                        <div style="background:var(--yellow-light);border:2px solid var(--yellow);
                             border-radius:14px;padding:0.6rem 1rem;margin:0.3rem 0;font-size:0.88rem">
                            🤩 <strong>Fun Fact:</strong> {data['fun_fact']}
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    # ─── Input Area ───────────────────────────────────────────────────────────
    st.markdown("---")
    placeholder = {
        "solver": "Type your math problem here... e.g. 'Solve 2x + 5 = 15' or 'What is 15% of 240?'",
        "concept": "Ask about a concept... e.g. 'Explain what is Pythagoras theorem' or 'What are fractions?'",
    }

    st.markdown("#### ✏️ Ask Your Question")
    tab1, tab2, tab3 = st.tabs(["⌨️ Type", "🎙️ Voice", "📸 Photo"])

    user_text = None
    image_b64 = None

    with tab1:
        text_input = st.text_area("Type your question",
                                   placeholder=placeholder[st.session_state.mode],
                                   height=100, label_visibility="collapsed")
        if st.button("🚀 Ask MathMagic!", use_container_width=True):
            if text_input.strip():
                user_text = text_input.strip()

    with tab2:
        audio_input = st.audio_input("Record your question")
        if audio_input:
            with st.spinner("🎧 Listening..."):
                try:
                    user_text = transcribe_audio(client, audio_input.read())
                    st.success(f"🎤 You said: *\"{user_text}\"*")
                except Exception as e:
                    st.error(f"Could not transcribe: {e}")

    with tab3:
        uploaded = st.file_uploader("Upload a photo of your problem",
                                     type=["jpg", "jpeg", "png"],
                                     label_visibility="collapsed")
        photo_note = st.text_input("Any extra note about the photo?",
                                    placeholder="e.g. 'Solve question 3' or 'Explain this diagram'")
        if uploaded and st.button("🔍 Solve from Photo!", use_container_width=True):
            image_b64 = encode_image(uploaded.read())
            user_text = photo_note if photo_note.strip() else "Please solve the math problem shown in this image step by step."

    # ─── Process & Respond ────────────────────────────────────────────────────
    if user_text:
        display_text = user_text if not image_b64 else f"📸 [Photo uploaded] {user_text}"
        st.session_state.messages.append({"role": "user", "content": display_text})

        with st.spinner("🧮 MathMagic is thinking..."):
            try:
                if st.session_state.mode == "solver":
                    system_prompt = build_solver_prompt(grade, language)
                else:
                    system_prompt = build_concept_prompt(grade, language)

                raw = call_llm(client, system_prompt, user_text, image_b64)
                parsed = parse_json_response(raw)

                if parsed:
                    reply_text = parsed.get("reply", "") + " " + parsed.get("answer", "")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reply_text,
                        "parsed": parsed,
                    })
                    if voice_reply:
                        speak_text = parsed.get("reply", "") + " " + " ".join(parsed.get("steps", [])) + " " + parsed.get("answer", "")
                        speak(speak_text[:500], voice_choice)
                else:
                    st.session_state.messages.append({"role": "assistant", "content": raw})
                    if voice_reply:
                        speak(raw[:500], voice_choice)

            except Exception as e:
                st.error(f"⚠️ Error: {e}")

        st.rerun()
