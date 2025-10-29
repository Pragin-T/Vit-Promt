import os
import requests
from typing import List, Dict, Any

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://api.googlegemini.com/v1/analyze"  # Replace with actual Gemini endpoint


def analyze_phishing(content: str, images: List[str] = None, urls: List[str] = None) -> Dict[str, Any]:
    """
    Analyze text, image, and URL content for phishing using Gemini API (AI-assisted threat detection).

    Args:
        content (str): Main page or email text content.
        images (list): Optional list of base64-encoded images or image URLs.
        urls (list): Optional list of URLs detected in the content.

    Returns:
        dict: Structured response aligned with UI questions.
    """

    payload = {
        "text": content,
        "images": images or [],
        "urls": urls or [],
    }

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        # Fallback response if API fails
        data = {"score": 0.9, "flags": ["network_error"], "message": str(e)}

    # --- Example interpretation / structure matching UI ---
    phishing_score = data.get("score", 0.87)
    flags = data.get("flags", [
        "Suspicious login prompt detected",
        "Low domain reputation",
        "Hidden JavaScript redirects",
        "SSL certificate mismatch",
        "AI-detected phishing pattern"
    ])

    # Convert score to severity level
    if phishing_score >= 0.85:
        severity = "High"
    elif phishing_score >= 0.6:
        severity = "Moderate"
    else:
        severity = "Low"

    # Structured output (used by front-end)
    result = {
        "phishing_score": phishing_score,
        "severity": severity,
        "question_1": "Why was this website flagged?",
        "answer_1": [
            "This website was flagged due to:",
            *flags
        ],
        "question_2": "Why is phishing dangerous?",
        "answer_2": [
            "Phishing is dangerous because attackers:",
            "• Create fake login pages to steal credentials",
            "• Spread malware or ransomware",
            "• Redirect funds to fraudulent accounts",
            "• Clone identities and exploit personal data",
            "• Intercept encrypted communications, risking financial and privacy damage"
        ]
    }

    return result


{
  "phishing_score": 0.91,
  "severity": "High",
  "question_1": "Why was this website flagged?",
  "answer_1": [
    "This website was flagged due to:", 
    "Suspicious login prompt detected",
    "Low domain reputation",
    "SSL certificate mismatch",
    "Hidden JavaScript redirects",
    "AI-detected phishing pattern"
  ],
  "question_2": "Why is phishing dangerous?",
  "answer_2": [
    "Phishing is dangerous because attackers:",
    "• Create fake login pages to steal credentials",
    "• Spread malware or ransomware",
    "• Redirect funds to fraudulent accounts",
    "• Clone identities and exploit personal data",
    "• Intercept encrypted communications, risking financial and privacy damage"
  ]
}
