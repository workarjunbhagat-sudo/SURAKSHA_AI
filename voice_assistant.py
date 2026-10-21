import streamlit as st
import asyncio
import html
import json
import tempfile
from pathlib import Path

VOICE_MAP = {
    "English": "en-IN-NeerjaNeural",   # Indian English female neural voice
    "हिंदी": "hi-IN-SwaraNeural",      # Hindi female neural voice
    "Hinglish": "hi-IN-SwaraNeural",   # Hindi female voice for natural Hinglish
}

def answer_for(text, language="English"):
    t = (text or "").lower()
    if any(k in t for k in ["otp","pin","cvv","password","पासवर्ड","ओटीपी","पिन"]):
        return {
            "English":"Never share your OTP, PIN, CVV or password. Stop the conversation and verify the request through the official app or website.",
            "हिंदी":"OTP, PIN, CVV या पासवर्ड कभी साझा न करें। बातचीत रोकें और अनुरोध को आधिकारिक ऐप या वेबसाइट से स्वयं सत्यापित करें।",
            "Hinglish":"OTP, PIN, CVV ya password kabhi share mat karo. Conversation rok do aur official app ya website se request verify karo."
        }[language]
    if any(k in t for k in ["link","url","website","click","लिंक","वेबसाइट"]):
        return {
            "English":"Do not click an unexpected link. Open the official app or type the official website yourself and check the alert there.",
            "हिंदी":"अनजान या संदिग्ध लिंक पर क्लिक न करें। आधिकारिक ऐप खोलें या वेबसाइट खुद टाइप करके वहां जांच करें।",
            "Hinglish":"Unknown ya suspicious link par click mat karo. Official app ya website khud open karke verify karo."
        }[language]
    if any(k in t for k in ["money","payment","upi","paise","पैसे","भुगतान"]):
        return {
            "English":"Do not transfer money because of urgency or threats. Independently verify the recipient and reason for payment first.",
            "हिंदी":"जल्दबाजी या धमकी के कारण पैसे ट्रांसफर न करें। भुगतान से पहले प्राप्तकर्ता और कारण को स्वतंत्र रूप से सत्यापित करें।",
            "Hinglish":"Urgency ya threat ki wajah se paise transfer mat karo. Payment se pehle receiver aur reason independently verify karo."
        }[language]
    if any(k in t for k in ["scam","fraud","धोखा","फ्रॉड"]):
        return {
            "English":"Paste the suspicious message, upload its screenshot, or paste its URL into the relevant SURAKSHA checker.",
            "हिंदी":"संदिग्ध संदेश पेस्ट करें, उसका स्क्रीनशॉट अपलोड करें या URL को संबंधित SURAKSHA checker में डालें।",
            "Hinglish":"Suspicious message paste karo, screenshot upload karo ya URL ko relevant SURAKSHA checker mein daalo."
        }[language]
    return {
        "English":"Pause before acting. Do not share sensitive information. Verify unexpected requests using an official source you find independently.",
        "हिंदी":"कोई भी कदम उठाने से पहले रुकें। संवेदनशील जानकारी साझा न करें। अनजान अनुरोध को स्वतंत्र आधिकारिक स्रोत से सत्यापित करें।",
        "Hinglish":"Action lene se pehle pause karo. Sensitive information share mat karo. Unexpected request ko independently official source se verify karo."
    }[language]

async def _make_female_audio(text, language, output_file):
    import edge_tts
    voice = VOICE_MAP.get(language, VOICE_MAP["English"])
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate="-8%",
        volume="+0%",
        pitch="+0Hz"
    )
    await communicate.save(output_file)

def make_female_audio(text, language):
    """Generate a clear female neural voice MP3. Returns path or None."""
    try:
        fd, name = tempfile.mkstemp(suffix=".mp3")
        import os
        os.close(fd)
        asyncio.run(_make_female_audio(text, language, name))
        return name
    except Exception:
        return None

def voice_widget(language):
    lang = {"English":"en-IN","हिंदी":"hi-IN","Hinglish":"hi-IN"}.get(language,"en-IN")
    return f"""
    <div style="border:1px solid #d8e1ee;border-radius:18px;padding:20px;background:#f8fbff;font-family:Arial">
      <h3 style="margin:0 0 8px">🎙️ Voice Assistant</h3>
      <div id="status" style="margin:8px 0;color:#46566b">
        🎙️ Click the microphone and speak clearly.
      </div>
      <button id="mic" style="font-size:18px;padding:14px 20px;border-radius:12px;border:0;cursor:pointer">
        🎙️ Start Listening
      </button>
      <div id="heard" style="margin-top:15px;font-weight:600"></div>
      <script>
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const btn=document.getElementById("mic"), status=document.getElementById("status");
      const heard=document.getElementById("heard");
      const LANG={json.dumps(lang)};
      if(!SpeechRecognition){{
        btn.disabled=true;
        status.textContent="⚠️ Voice input is unavailable here. Use the Type mode or Chrome/Edge.";
      }} else {{
        btn.onclick=()=>{{
          const r=new SpeechRecognition();
          r.lang=LANG; r.interimResults=false; r.continuous=false; r.maxAlternatives=1;
          status.textContent="🎧 Listening... Please speak.";
          btn.disabled=true;
          r.onresult=(e)=>{{
            heard.textContent="📝 "+e.results[0][0].transcript;
            status.textContent="✅ Voice captured. Use the response shown below.";
          }};
          r.onerror=(e)=>{{
            status.textContent="⚠️ "+e.error+". Please allow microphone access and try again.";
          }};
          r.onend=()=>{{btn.disabled=false;}};
          r.start();
        }};
      }}
      </script>
    </div>
    """

def voice_response(text, language):
    """Generate and display a female neural response, with browser fallback."""
    audio_path = make_female_audio(text, language)
    if audio_path:
        st.audio(audio_path, format="audio/mp3")
        st.caption({
            "English":"🔊 Female Indian English voice • Senior-friendly pace",
            "हिंदी":"🔊 महिला हिंदी आवाज़ • वरिष्ठ नागरिकों के लिए धीमी और स्पष्ट गति",
            "Hinglish":"🔊 Female Hindi voice • Senior-friendly clear pace"
        }[language])
        return True

    # Fallback if neural voice service is unavailable.
    safe = html.escape(text).replace("\\", "\\\\").replace("'", "\\'")
    browser_lang = {"English":"en-IN","हिंदी":"hi-IN","Hinglish":"hi-IN"}.get(language,"en-IN")
    st.components.v1.html(f"""
    <script>
    const voices=window.speechSynthesis.getVoices();
    const msg=new SpeechSynthesisUtterance('{safe}');
    msg.lang='{browser_lang}';
    msg.rate=0.85;
    msg.pitch=1.05;
    const preferred=voices.find(v =>
      (v.lang||'').toLowerCase().startsWith('{browser_lang[:2].lower()}') &&
      /female|zira|heera|susan|neerja|swara/i.test(v.name)
    );
    if(preferred) msg.voice=preferred;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
    </script>
    """, height=50)
    st.warning("Neural female voice is temporarily unavailable, so the browser voice fallback is being used.")
    return False
