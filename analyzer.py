import re
from urllib.parse import urlparse
from ml_engine import analyze_ml

DEMO_MESSAGES = {
    "Fake KYC / bank message": """🚨 URGENT: Your bank account will be BLOCKED within 2 hours due to incomplete KYC verification.

To prevent suspension, verify your account immediately:
http://sbi-kyc-verification.example/demo

You must enter your Aadhaar number, ATM PIN and OTP to complete verification.
Failure to verify may result in a ₹10,000 penalty.
— KYC Department""",
    "Digital arrest style": """URGENT NOTICE: Your identity has been linked to a cyber crime case. A police officer says you must join a video call immediately and transfer money for verification or face arrest.""",
    "Prize scam": """Congratulations! You have won a ₹50,000 prize. Pay a small processing fee and send your bank details and OTP to claim the reward today.""",
    "Lower-risk example": """Your college assignment submission deadline is Monday. Please upload your file on the official student portal before 11:59 PM."""
}

def analyze_message(text: str):
    return analyze_ml(text)

def analyze_url(url: str):
    risk = 0
    indicators = []
    u = url.strip()
    if not u:
        return {"risk": 0, "indicators": []}
    if not re.match(r"^https?://", u, re.I):
        risk += 15
        indicators.append({"name": "Missing URL scheme", "explanation": "The link does not clearly use HTTP or HTTPS."})
    try:
        parsed = urlparse(u if re.match(r"^https?://", u, re.I) else "http://" + u)
        host = parsed.hostname or ""
        if "@" in u:
            risk += 20
            indicators.append({"name": "Obfuscated URL", "explanation": "The URL contains @, which can hide the actual destination."})
        if host.startswith("xn--") or ".xn--" in host:
            risk += 20
            indicators.append({"name": "Punycode domain", "explanation": "The domain uses punycode, which deserves extra verification."})
        if len(host) > 35:
            risk += 15
            indicators.append({"name": "Long domain", "explanation": "An unusually long domain can be a warning sign."})
        if re.fullmatch(r"\d+(?:\.\d+){3}", host):
            risk += 15
            indicators.append({"name": "IP-address destination", "explanation": "The link points directly to an IP address instead of a normal domain name."})
        if parsed.port not in (None, 80, 443):
            risk += 10
            indicators.append({"name": "Unusual port", "explanation": "The URL uses a non-standard web port and should be verified independently."})
        if host.count(".") >= 4:
            risk += 8
            indicators.append({"name": "Many subdomains", "explanation": "Multiple nested subdomains can make a destination harder to verify."})
        if u.lower().startswith("http://"):
            risk += 10
            indicators.append({"name": "Unencrypted HTTP", "explanation": "The link does not use HTTPS. Do not treat this alone as proof of fraud."})
        if any(short in host.lower() for short in ["bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly"]):
            risk += 15
            indicators.append({"name": "URL shortener", "explanation": "A shortened link hides the final destination, so verify it before opening."})
        if any(k in u.lower() for k in ["verify", "kyc", "login", "secure", "update", "reward", "claim"]):
            risk += 15
            indicators.append({"name": "Sensitive-action keywords", "explanation": "The URL contains words commonly used in unsolicited verification or reward links."})
        if host.endswith(".example") or host.endswith(".test"):
            risk += 10
            indicators.append({"name": "Reserved demo/test domain", "explanation": "This is a reserved domain used for examples or testing."})
    except Exception:
        risk += 20
        indicators.append({"name": "Malformed URL", "explanation": "The URL could not be parsed normally."})
    return {"risk": min(risk, 100), "indicators": indicators}
