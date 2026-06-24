# 🎭 FailWhisperer
> AI-Powered Playwright Test Failure Analyst

FailWhisperer reads your Playwright test error logs and instantly tells you **why it failed**, **whether it's flaky**, and **exactly how to fix it** — powered by LLaMA 3.3 70B via Groq API.

---

## 🚀 Demo

Paste a Playwright error → Click Analyze → Get AI diagnosis in seconds!

**Supported error types:**
- ⏱️ Timeout errors
- 🔍 Locator failures  
- ❗ Assertion errors
- 🌐 Network errors

---

## ✨ Features

- 🤖 **AI Diagnosis** — LLaMA 3.3 70B analyzes your error
- 🏷️ **Error Classification** — Timeout / Locator / Assertion / Network
- 🔧 **Suggested Fix** — Exact code to fix the failure
- ⚠️ **Flaky Detection** — Identifies potentially flaky tests
- 📊 **Confidence Score** — High / Medium / Low with progress bar
- 📋 **Copy Fix** — One click copies the fix to clipboard
- 🕐 **History Panel** — Last 5 analyses saved in browser
- ⏳ **Loading Skeleton** — Smooth animation while AI thinks

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + Tailwind CSS v4 |
| Backend | FastAPI (Python) |
| AI Model | LLaMA 3.3 70B via Groq API |
| HTTP Client | Axios |
| Styling | Tailwind CSS v4 |

---

## 📁 Project Structure

FailWhisperer/

├── backend/

│   ├── main.py          # FastAPI server

│   ├── analyzer.py      # AI brain — Groq integration

│   ├── requirements.txt # Python dependencies

│   └── .env             # API keys (not committed)

└── frontend/

├── src/

│   └── App.jsx      # React UI — all components

├── index.css        # Tailwind CSS

└── package.json     # Node dependencies


---

## ⚙️ Setup & Run Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- Free Groq API key → [console.groq.com](https://console.groq.com)

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Create .env file
echo GROQ_API_KEY=your_key_here > .env

# Run FastAPI
uvicorn main:app --reload
# → http://localhost:8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## 🧪 Test It

Paste this in the error box:
TimeoutError: locator.click: Timeout 30000ms exceeded.

Call log:

waiting for locator('#submit-btn')

at LoginPage.clickSubmit (tests/login.spec.ts:45:20)

Expected output:
- 🔴 **LOCATOR** badge
- Root cause explanation
- Fix: `await page.waitForSelector('#submit-btn', { visible: true })`
- Confidence: **HIGH**

---

## 👩‍💻 Built By

**Sangeetha H S** — QA Automation Engineer → Gen AI Developer  
4+ years in Playwright, TypeScript, REST API testing  
Building AI-powered QA tools

[![GitHub](https://img.shields.io/badge/GitHub-SangeethaSan21-black?logo=github)](https://github.com/SangeethaSan21)

---

## 📄 License

MIT License — free to use and modify
