# SURAKSHA_AI
SURAKSHA AI 🛡️ — An AI-powered digital safety companion that detects potential scams, analyzes suspicious messages and URLs, supports multilingual users, and helps people stay safe online.
# 🛡️ SURAKSHA AI — Your Digital Safety Companion

**Detect suspicious messages. Understand digital threats. Stay safer online.**

SURAKSHA AI is an AI-powered digital safety application designed to help users identify potential scams, suspicious messages, and risky URLs. It combines machine learning with explainable safety rules to make cybersecurity more accessible, understandable, and practical.

## 🚀 Key Features

- **📩 Scam Message Detection:** Analyze messages for suspicious language, fraud indicators, and potential scam patterns.
- **🔗 URL Safety Analysis:** Examine URL structures for common warning signs without automatically opening the destination.
- **🖼️ Screenshot Analysis:** Extract text from screenshots using OCR and analyze the extracted content.
- **🌐 Multilingual Interface:** Supports English, Hindi, and Hinglish.
- **🤖 AI Safety Assistant:** Optional AI-powered assistance for understanding digital threats.
- **👴 Senior Mode:** A simplified experience designed to make online safety guidance easier to understand.
- **🧠 Scam Awareness Trainer:** Learn to recognize common fraud tactics through interactive examples.
- **🛡️ Incident Response Guidance:** Get practical next steps when you encounter a suspected scam.
- **📊 Additional Tools:** Explore features such as batch scanning, message comparison, history, reports, and safety readiness where available in the application.

## 🧠 How It Works

SURAKSHA AI combines machine learning and rule-based analysis to assess potentially suspicious content.

1. **Input:** The user submits a message, URL, or supported screenshot.
2. **Preprocessing:** Text is cleaned and prepared for analysis. Screenshot text can be extracted using OCR.
3. **Machine Learning:** A TF-IDF text representation and Logistic Regression classifier help identify suspicious language patterns.
4. **Rule-Based Analysis:** Additional safety rules examine indicators such as urgency, requests for sensitive information, and suspicious URL structures.
5. **Results:** The application presents an assessment and safety guidance to help the user make a more informed decision.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| Machine Learning | Scikit-learn |
| Text Processing | TF-IDF |
| Classification | Logistic Regression |
| Screenshot Text Extraction | Tesseract OCR |
| Optional API Backend | FastAPI |
| API Server | Uvicorn |

## 📂 Project Structure

```text
SURAKSHA-AI/
├── app.py
├── requirements.txt
├── requirements-api.txt
├── packages.txt
├── render.yaml
├── analyzer.py
├── api_client.py
├── backend/
├── .streamlit/
├── tests/
└── DEPLOY_GUIDE.md
```

*The exact structure may include additional modules and assets depending on the project version.*

## 💻 Run Locally

### 1. Download the project

Download the ZIP file or clone your repository:

```bash
git clone https://github.com/YOUR-USERNAME/suraksha-ai.git
cd suraksha-ai
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## ☁️ Deployment

SURAKSHA AI can be deployed using **Streamlit Community Cloud**.

1. Upload the project files to a GitHub repository.
2. Visit https://share.streamlit.io/
3. Sign in with GitHub and create a new app.
4. Select your repository and the `main` branch.
5. Set the main file path to `app.py`.
6. Deploy the application.

For detailed instructions, see [`DEPLOY_GUIDE.md`](DEPLOY_GUIDE.md).

The optional FastAPI backend can be deployed separately on a compatible hosting service such as Render.

## 🔐 Security & Privacy

- Never enter real passwords, OTPs, banking credentials, or other sensitive information into a public demo.
- Keep API keys and secrets out of source code and GitHub commits.
- Configure optional service credentials through your hosting provider's secret-management settings.
- URL analysis uses structural indicators and should not be interpreted as a guarantee that a website is safe.
- Machine learning predictions and rule-based assessments can produce false positives and false negatives.

## ⚠️ Important Disclaimer

SURAKSHA AI is an educational and preventive cybersecurity project. It is intended to support awareness and preliminary scam assessment, not replace professional security analysis or official reporting channels.

A message classified as safe may still be fraudulent, and a suspicious classification does not prove that a scam has occurred. Do not rely on this application as the sole basis for financial or security decisions.

## 🎯 Project Goals

- Make digital safety tools more accessible.
- Improve awareness of phishing, impersonation, and online fraud.
- Provide understandable explanations instead of unexplained predictions.
- Encourage safer online habits across different language preferences.

## 🔮 Future Improvements

- Larger and more diverse real-world datasets.
- More robust multilingual scam detection.
- Improved explainability and model evaluation.
- Additional threat intelligence integrations.
- Expanded accessibility and educational features.

## 👨‍💻 Project Information

**Project:** SURAKSHA AI — Your Digital Safety Companion  
**Category:** Artificial Intelligence, Machine Learning & Cybersecurity  
**Interface:** Streamlit  
**Backend:** Optional FastAPI

Built as a student project to explore practical AI applications for digital safety.

---

**If you find this project useful, consider giving the repository a ⭐ on GitHub!**

