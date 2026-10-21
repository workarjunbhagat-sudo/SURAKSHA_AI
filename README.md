# SURAKSHA AI v2 — Screenshot OCR Upgrade

SURAKSHA AI is a senior-friendly digital safety companion prototype for detecting suspicious scam messages and explaining warning signs.

## What is new in v2?

**Screenshot → OCR → Scam Analysis**

1. Upload a WhatsApp/SMS/email screenshot.
2. SURAKSHA extracts the visible text using Tesseract OCR.
3. The extracted text is sent to the existing explainable scam detector.
4. The app shows risk level, category, indicators, and safety actions.

## Windows setup

### 1. Install Python packages

Open PowerShell inside this folder:

```powershell
python -m pip install -r requirements.txt
```

### 2. Install Tesseract OCR

The Python package `pytesseract` is only a connector. Windows also needs the Tesseract OCR program.

Official Tesseract project:
https://github.com/tesseract-ocr/tesseract

A common Windows installer is available from the UB Mannheim build page:
https://github.com/UB-Mannheim/tesseract/wiki

During installation, the default location is usually:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

SURAKSHA checks that location automatically.

### 3. Restart the app

Stop Streamlit with:

```text
Ctrl + C
```

Then start again:

```powershell
python -m streamlit run app.py
```

## Expo demo

Use a screenshot containing the fictional demo KYC scam message.

Recommended demo flow:

**Upload screenshot → Extract & Analyze → OCR text appears → HIGH RISK → Bank/KYC category → warning indicators → safe actions**

Do not use real OTPs, PINs, passwords, banking credentials, or private personal information.

## Important limitation

OCR accuracy depends on image quality, font size, lighting, and language. This prototype is an educational demonstration and does not guarantee that a message is legitimate or fraudulent.

## Project structure

```text
SURAKSHA_AI/
├── app.py
├── analyzer.py
├── ocr_engine.py
├── requirements.txt
├── README.md
├── sample_messages.txt
└── .gitignore
```


## v3 — AI/DS upgrade

The message detector now uses a real local machine-learning pipeline:

```text
Message / OCR text
       ↓
Text normalization
       ↓
TF-IDF (unigrams + bigrams)
       ↓
Logistic Regression classifier
       ↓
ML suspicious probability
       +
Explainable rule indicators
       ↓
Combined risk score + category + safety guidance
```

The training data is intentionally small and curated for an educational expo prototype. It is **not** production-grade fraud detection. A future version should train and evaluate on a much larger, representative labeled dataset and report precision, recall, F1 and confusion matrix.

No cloud API or paid AI service is required for this ML layer.


## v4 — Evaluation upgrade

The app now includes a **Model Performance** tab showing:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix
- Training/test sample counts

The model uses a stratified held-out test split (`random_state=42`). Metrics are computed locally when the app starts.

**Expo note:** Present these as metrics on the curated educational demo dataset, not as real-world fraud-detection performance.


## v5 — Expo feature pack

New features:
- 🛡️ Safety Center with “I may have been scammed” guidance
- 👨‍👩‍👧 Family Protection Alert generator
- 📚 Scam Library covering common scam patterns
- 📋 Session history and downloadable demo incident report
- 🔗 Expanded offline URL heuristics (IP address, HTTP, unusual port, shorteners, subdomains)
- 🎬 One-click expo demo scenarios
- 🖼️ Included `demo_scam_screenshot.png` containing fictional data for OCR demonstrations
- Senior Mode remains available
- ML evaluation, confusion matrix and explainable indicators remain available

### Suggested 3-minute expo flow
1. Load **Fake KYC / bank message** from the sidebar.
2. Analyze it → show risk + explanation + ML probability.
3. Open **Screenshot** → upload `demo_scam_screenshot.png` after Tesseract is installed.
4. Open **Link** → test the demo URL.
5. Open **Model Performance** → explain TF-IDF + Logistic Regression + held-out metrics.
6. Open **Safety Center** → generate a family alert.
7. Open **Scam Library** → show how the system educates users.

All detection is local and rule/ML based. No cloud API key is required.


## v6 — Hindi/English + Voice Assistant

### 🌐 Language
Use the sidebar selector:
- English
- हिंदी
- Hinglish

SURAKSHA's safety guidance and voice assistant responses adapt to the selected language.

### 🎙️ Voice chatbot
Open **🗣️ Ask Suraksha**:
1. Select **Voice**.
2. Tap the microphone.
3. Ask your question.
4. SURAKSHA transcribes it and generates a safety response.
5. The browser reads the answer aloud using Speech Synthesis.

Voice transcription uses the SpeechRecognition Google recognizer, so the microphone-to-text step may require an internet connection. The spoken reply uses the browser and needs no API key.

### Expo demo
Try:
- English: "Someone is asking me for an OTP. What should I do?"
- हिंदी: "कोई मुझसे OTP मांग रहा है, मैं क्या करूं?"
- Hinglish: "Mujhe ek suspicious link aaya hai, kya karu?"

For the expo, demonstrate the same question in all three languages.

\n## v7 Performance + Reliable Browser Voice\n
- Full visible UI language switching for English / हिंदी / Hinglish.
- Browser-native microphone voice assistant for Chrome/Edge.
- Browser speech synthesis reads answers aloud.
- No PyAudio, PortAudio or microphone-driver installation is required.
- Voice demo works locally with rule-based safety responses, so it does not depend on an API key.
- Existing OCR, URL analysis, ML metrics, safety center, library, history and reports are retained.
\n### If the microphone does not start\n
1. Use the latest Chrome or Edge.
2. Click the microphone permission **Allow**.
3. Make sure Windows microphone permission is enabled.
4. Refresh the Streamlit page.
5. Use the **Type** mode as a fallback if browser speech recognition is unavailable.


## v8 — Senior-Friendly Female Voice

The voice assistant now uses Microsoft Edge TTS neural voices when internet access is available:
- English: `en-IN-NeerjaNeural` — Indian English female voice
- Hindi: `hi-IN-SwaraNeural` — Hindi female voice
- Hinglish: Hindi female neural voice for natural mixed-language speech

The speech rate is slowed slightly for senior-friendly clarity. A browser speech-synthesis fallback remains available.

### Voice demo
1. Select English, हिंदी or Hinglish.
2. Open Ask Suraksha.
3. Use Voice mode to speak.
4. Enter/confirm the recognized question in the response box.
5. Click **GET FEMALE VOICE ANSWER**.
6. SURAKSHA responds in the selected language with a clear female voice.


## v9 — Live AI Chat

The Ask Suraksha assistant now uses a real generative model instead of canned responses.

### OpenAI mode
1. Install requirements.
2. Start Streamlit.
3. Paste an OpenAI API key into the **Live AI Engine** box in the sidebar.
4. Ask a question.
5. Enable **Use live web search when needed** for current information.
6. Voice mode records from Streamlit's microphone widget, transcribes with `gpt-4o-mini-transcribe`, generates a dynamic answer, then speaks it with `gpt-4o-mini-tts`.

### Local mode
If no OpenAI key is supplied, SURAKSHA tries a local Ollama model (`llama3.2:3b` by default). Set `SURAKSHA_OLLAMA_MODEL` if a different installed model should be used.

The app still keeps the explainable scam detector separate from the LLM. The risk score is a signal, not proof of fraud.

## v10 Expo Features
- Safety Dashboard with live session statistics and recent activity
- Explainable Risk Breakdown for detected warning signals
- Incident Response Wizard for common scam situations
- Five-Second Call Safety Check
- Scam Awareness Trainer with 5 interactive scenarios and score
- JSON export of analysis history
- Existing v9 features retained: ML analysis, OCR, URL analysis, multilingual live AI, voice input/output, optional web search, family alert, scam library, history/report

## Recommended 3-minute expo demo
1. Dashboard — explain the problem and architecture.
2. Message Checker — load the fake KYC demo and show risk + indicators + explainability.
3. Screenshot — show OCR workflow if Tesseract is installed.
4. Ask Suraksha — ask a new question and demonstrate dynamic AI in English/Hindi/Hinglish.
5. Incident Response Wizard — show what happens after clicking a link or sharing a credential.
6. Scam Trainer — complete one scenario and show the safety score.

# SURAKSHA AI 2.0 — Hackathon Engineering Upgrade

This version adds an optional FastAPI service around the existing Streamlit prototype.
The Streamlit app still works if the API is offline; when `SURAKSHA_API_URL` is configured,
message and URL analyses use the API and gracefully fall back to local analysis if it is unavailable.

## New engineering features

- **FastAPI REST API** with interactive OpenAPI docs at `http://127.0.0.1:8000/docs`.
- **Message analysis endpoint**: `POST /v1/analyze/message`.
- **URL-string analysis endpoint**: `POST /v1/analyze/url`. It does not visit or follow the submitted URL.
- **Incident response endpoint**: `POST /v1/incident-response`, with English, Hindi, and Hinglish guidance.
- **Model metrics endpoint**: `GET /v1/model/metrics`, with explicit evaluation limitations.
- **Opt-in privacy-preserving history**: stores aggregate metadata only (risk, category, source, language, model); never stores raw message text or URLs.
- **History controls**: `GET /v1/history` and `DELETE /v1/history`.
- **Optional API key**: set `SURAKSHA_API_KEY` in a local `.env` file to protect `/v1` endpoints. `/health` remains public.
- **Automated API tests**: run with `python -m pytest -q`.
- **Model benchmarking script**: `python scripts/evaluate_models.py` (runs supported baseline comparisons on the bundled curated demo data; results are educational only).

## New interactive UI workflows

The upgraded Streamlit interface adds three workflows alongside the original scan and safety tools:

- **Batch Scan:** analyze up to 100 messages from pasted blocks or a CSV file, filter results by risk band, and export a CSV. Full message text is excluded from exports by default.
- **Compare:** analyze two messages side by side, compare risk scores, and see which warning indicators are shared or unique.
- **Safety Readiness:** complete a six-item digital-safety checklist, see progress, and download the checklist. It is self-reported guidance, not a device/security audit.

The visual style has also been refreshed with a responsive dashboard layout, refined cards, and clearer tabs. Message analysis is a prototype aid: a score is not proof of fraud or proof of safety. Avoid using real OTPs, passwords, account numbers, or other sensitive content in demos.

## Windows quick start

Open PowerShell in the folder containing `app.py` and `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
python -m pip install -r dev-requirements.txt
```

Run the existing UI:

```powershell
python -m streamlit run app.py
```

Run the API in a second PowerShell window in the same folder:

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000/docs` to try the endpoints. To connect the Streamlit app to the API, copy `.env.example` to `.env` and set `SURAKSHA_API_URL=http://127.0.0.1:8000`. Keep `.env` private and never commit real keys.

Run tests:

```powershell
python -m pytest -q
```

## Security and evaluation notes

- Do not paste real OTPs, PINs, passwords, or private banking details into demos.
- Keep the API bound to localhost for a college demo. Do not expose it publicly without proper authentication, TLS, rate limiting, monitoring, and deployment review.
- A URL is analyzed as text only; the API does not fetch it, reducing risk from malicious destinations and SSRF.
- History is opt-in and metadata-only. It is not a forensic evidence store.
- The bundled training data is a small curated prototype dataset. Metrics are not evidence of real-world performance. Before making production claims, use a larger, independently sourced and legally usable dataset, deduplicate it, prevent train/test leakage, and evaluate by language and scam category.
