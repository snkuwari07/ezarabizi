from flask import Flask, request, jsonify, send_from_directory
import re
import os
import uuid
import requests  # for calling the translation API

from gtts import gTTS

try:
    from flask_cors import CORS
except ImportError:
    CORS = None

# -------------------------------------------------
# APP SETUP
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

app = Flask(__name__)

if CORS is not None:
    CORS(app)  # allow Netlify / localhost to call the API

# -------------------------------------------------
# ARABIZI RULES
# -------------------------------------------------

MULTI_CHAR_RULES = [
    ("kh", "خ"),
    ("gh", "غ"),
    ("sh", "ش"),
    ("ch", "تش"),
    ("th", "ث"),
    ("dh", "ذ"),
    ("ei", "ي"),
    ("ee", "ي"),
]

SINGLE_CHAR_MAP = {
    "a": "ا",
    "b": "ب",
    "t": "ت",
    "j": "ج",
    "h": "ه",
    "7": "ح",
    "5": "خ",
    "d": "د",
    "r": "ر",
    "z": "ز",
    "s": "س",
    "9": "ص",
    "6": "ط",
    "3": "ع",
    "f": "ف",
    "q": "ق",
    "8": "ق",
    "k": "ك",
    "l": "ل",
    "m": "م",
    "n": "ن",
    "w": "و",
    "o": "و",
    "y": "ي",
    "e": "ي",
    "i": "ي",
    "u": "و",
    "2": "ء",
    "4": "ذ",
}

ARABIZI_SPECIAL_WORDS = {
    "7abibi": "حبيبي",
    "7abeby": "حبيبي",
    "ok": "تمام",
    "okay": "تمام",
    "oky": "تمام",
}


def translate_arabizi(text: str) -> str:
    """Arabizi -> Arabic transliteration."""
    result = text.lower()

    # multi-char patterns
    for pattern, repl in MULTI_CHAR_RULES:
        result = re.sub(pattern, repl, result)

    translated_words = []
    words = result.split()

    for word in words:
        if word in ARABIZI_SPECIAL_WORDS:
            translated_words.append(ARABIZI_SPECIAL_WORDS[word])
            continue

        arabic_word = []
        i = 0
        while i < len(word):
            # special example: 7alk -> حالك
            if word[i:i + 4] == "7alk":
                arabic_word.append("حالك")
                i += 4
                continue

            ch = word[i]
            if "\u0600" <= ch <= "\u06FF":
                arabic_word.append(ch)
            else:
                arabic_word.append(SINGLE_CHAR_MAP.get(ch, ch))
            i += 1

        translated_words.append("".join(arabic_word))

    return " ".join(translated_words)


def smart_correct_arabic(text: str) -> str:
    """Tiny word-level fixes."""
    word_map = {
        "انا": "أنا",
        "سوري": "آسف",
    }
    words = text.split()
    corrected_words = [word_map.get(w, w) for w in words]
    return " ".join(corrected_words)


def translate_to_english(text: str) -> str:
    """
    Arabic -> English using LibreTranslate (works better than googletrans on Render).
    """
    if not text.strip():
        return ""

    try:
        r = requests.post(
            "https://libretranslate.de/translate",
            data={
                "q": text,
                "source": "ar",
                "target": "en",
                "format": "text",
            },
            timeout=10,
        )
        data = r.json()
        return data.get("translatedText", "")
    except Exception as e:
        print("LibreTranslate error:", repr(e))
        return ""


# -------------------------------------------------
# ROUTES
# -------------------------------------------------

@app.route("/")
def index():
    return "EzArabizi API running."


@app.route("/translate", methods=["POST"])
def translate_endpoint():
    data = request.get_json() or {}
    print("🔹 /translate called. Raw data:", data)

    arabizi_text = data.get("text", "").strip()
    if not arabizi_text:
        return jsonify({"error": "Missing 'text'"}), 400

    print("🔹 Received text:", repr(arabizi_text))

    # 1) Arabizi -> Arabic
    arabic_raw = translate_arabizi(arabizi_text)
    arabic_corrected = smart_correct_arabic(arabic_raw)
    print("🔹 arabic_raw:", arabic_raw)
    print("🔹 arabic_corrected:", arabic_corrected)

    # 2) Arabic -> English
    english_text = translate_to_english(arabic_corrected)
    if not english_text:
        english_text = "English translation unavailable."
    print("🔹 english_text:", english_text)

    # 3) Audio with gTTS
    arabic_audio_url = None
    english_audio_url = None

    try:
        if arabic_corrected.strip():
            arabic_filename = f"arabic_{uuid.uuid4().hex}.mp3"
            arabic_path = os.path.join(AUDIO_DIR, arabic_filename)
            gTTS(arabic_corrected, lang="ar").save(arabic_path)
            arabic_audio_url = f"/audio/{arabic_filename}"

        if english_text and english_text.strip():
            english_filename = f"english_{uuid.uuid4().hex}.mp3"
            english_path = os.path.join(AUDIO_DIR, english_filename)
            gTTS(english_text, lang="en").save(english_path)
            english_audio_url = f"/audio/{english_filename}"
    except Exception as e:
        print("TTS error:", repr(e))

    response = {
        "input": arabizi_text,
        "arabic_raw": arabic_raw,
        "arabic_corrected": arabic_corrected,
        "english": english_text,
        "arabic_audio_url": arabic_audio_url,
        "english_audio_url": english_audio_url,
    }
    print("🔹 Response JSON:", response)
    return jsonify(response)


@app.route("/audio/<path:filename>")
def get_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)


@app.route("/ping")
def ping():
    return jsonify({"message": "ok"})


if __name__ == "__main__":
    # local testing
    app.run(host="127.0.0.1", port=5000, debug=True)
