# 🧮 MathMagic — AI Math Tutor for Grade 1 to 12

An AI-powered math tutor built with **Streamlit**, **Groq API (Llama 3.3-70B + Whisper)**, and **Edge TTS**.

## Features
- 🔍 **Problem Solver** — step-by-step solutions for any math problem
- 📖 **Concept Explainer** — explains any math topic with real-life analogies
- 📝 **Practice Quiz Generator** — generates 5-question quizzes on any topic
- 🎙️ **Voice Input** — speak your question via Groq Whisper
- 📸 **Photo Upload** — snap a photo of a textbook problem
- 🌐 **Multilingual** — English, Hindi, Gujarati, or bilingual
- 🔊 **Voice Reply** — AI reads the solution aloud
- 🎓 **Grade 1–12** — adapts explanation complexity per grade
- 🌈 **Fun, colorful UI** — kid-friendly design

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push to GitHub (public repo)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set `app.py` as main file
4. In **Advanced Settings → Secrets**, add:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```
5. Click **Deploy!**

## Get Free Groq API Key
👉 [console.groq.com](https://console.groq.com)

## Models Used
| Component | Model |
|---|---|
| Math reasoning | `llama-3.3-70b-versatile` (Groq) |
| Voice input | `whisper-large-v3` (Groq) |
| Voice output | Edge TTS (Microsoft, free) |
| Photo reading | Llama vision via base64 image |

## Project Structure
```
math_tutor/
├── app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```
