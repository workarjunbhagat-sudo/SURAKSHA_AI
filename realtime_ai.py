
import os
import requests
import streamlit as st

LANGUAGE_INSTRUCTIONS = {
    "English": "Reply in clear, simple Indian English. Use short sentences and explain unfamiliar technical terms.",
    "हिंदी": "Reply in simple Hindi using Devanagari. Use short, clear sentences suitable for a senior citizen.",
    "Hinglish": "Reply in natural Hinglish using Roman Hindi with common English words. Keep it simple and easy for a senior citizen."
}

SYSTEM = """You are SURAKSHA AI, a digital safety companion for senior citizens in India.
Your job is to answer the user's actual question dynamically, not from a fixed answer list.
Be calm, respectful, concise, and practical.

SAFETY RULES:
- Never ask the user to reveal OTPs, PINs, CVVs, passwords, UPI PINs, full card numbers, or other secrets.
- Never tell the user that a message is definitely a scam based only on text. Say "suspicious", "potentially fraudulent", or explain what evidence is present.
- For urgent financial, banking, government, police, KYC, courier, investment, or payment claims, recommend independent verification through an official app, website, or trusted phone number.
- If the user says they already shared credentials or transferred money, give immediate containment steps and advise contacting the real bank/payment provider through an independently verified channel.
- Do not invent phone numbers, reporting portals, laws, or official policies.
- If current information is needed and web search is enabled, use it and clearly distinguish current information from general guidance.
- Do not provide instructions that help someone commit fraud or evade fraud detection.

""" 

def _openai_client(api_key):
    from openai import OpenAI
    return OpenAI(api_key=api_key)

def ask_openai(question, language, api_key, risk_context="", web_search=False, history=None):
    client = _openai_client(api_key)
    instructions = SYSTEM + "\n" + LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["English"])
    if risk_context:
        instructions += "\n\nThe app's separate safety analyzer produced this context. Treat it as a signal, not proof:\n" + risk_context
    input_items = []
    for h in (history or [])[-8:]:
        input_items.append({"role": h["role"], "content": h["content"]})
    input_items.append({"role": "user", "content": question})
    kwargs = {
        "model": "gpt-5.6-luna",
        "instructions": instructions,
        "input": input_items,
        "max_output_tokens": 700,
    }
    if web_search:
        kwargs["tools"] = [{"type": "web_search"}]
    response = client.responses.create(**kwargs)
    return response.output_text.strip()

def transcribe_openai(audio_file, language, api_key):
    client = _openai_client(api_key)
    lang = {"English":"en", "हिंदी":"hi", "Hinglish":"hi"}.get(language, "en")
    audio_file.seek(0)
    result = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file,
        language=lang
    )
    return result.text.strip()

def speak_openai(text, language, api_key):
    from pathlib import Path
    import tempfile
    client = _openai_client(api_key)
    fd, path = tempfile.mkstemp(suffix=".mp3")
    import os as _os
    _os.close(fd)
    instructions = {
        "English": "Speak as a warm, calm, clear female-style assistant. Use a slightly slow pace for senior citizens. Pronounce Indian names and common Indian English naturally.",
        "हिंदी": "Speak as a warm, calm, clear Hindi female-style assistant. Use a slightly slow pace for senior citizens. Pronounce Hindi clearly and naturally.",
        "Hinglish": "Speak as a warm, calm, clear female-style assistant. Use a slightly slow pace for senior citizens. Speak natural Hinglish with clear Roman-Hindi-style pronunciation."
    }.get(language, "Speak clearly and slowly for a senior citizen.")
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text[:4096],
        instructions=instructions,
        response_format="mp3",
        speed=0.88
    )
    speech.write_to_file(path)
    return path

def ask_ollama(question, language, history=None, risk_context=""):
    model = os.getenv("SURAKSHA_OLLAMA_MODEL", "llama3.2:3b")
    messages = [{"role":"system","content":SYSTEM + "\n" + LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["English"])}]
    if risk_context:
        messages[0]["content"] += "\nSafety analyzer context:\n" + risk_context
    messages += [{"role":h["role"],"content":h["content"]} for h in (history or [])[-8:]]
    messages.append({"role":"user","content":question})
    r = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": model, "messages": messages, "stream": False},
        timeout=90
    )
    r.raise_for_status()
    return r.json()["message"]["content"].strip()

def dynamic_answer(question, language, api_key="", risk_context="", web_search=False, history=None):
    if api_key.strip():
        return ask_openai(question, language, api_key.strip(), risk_context, web_search, history), "OpenAI"
    # No API key: use local Ollama if available. This is still a real generated answer.
    try:
        return ask_ollama(question, language, history, risk_context), "Ollama local"
    except Exception as e:
        raise RuntimeError(
            "No AI provider is connected. Add an OpenAI API key in the sidebar, "
            "or install/start Ollama with a local model. The chatbot no longer uses fixed canned replies."
        ) from e
