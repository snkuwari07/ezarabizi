from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)


def normalize(text: str) -> str:
    # Lowercase + remove extra spaces
    return " ".join(text.strip().lower().split())


PHRASES = {
    # ----- Your phrases -----
    "salam 3lykm": {
        "arabic": "السلام عليكم",
        "english": "Peace be upon you",
        "arabic_audio": "/static/audio/salam_3lykm_ar.mp3",
        "english_audio": "/static/audio/salam_3lykm_en.mp3",
    },
    "kif 7alk": {
        "arabic": "كيف حالك؟",
        "english": "How are you?",
        "arabic_audio": "/static/audio/kif_7alk_ar.mp3",
        "english_audio": "/static/audio/kif_7alk_en.mp3",
    },
    "ana b5eir": {
        "arabic": "أنا بخير",
        "english": "I'm fine",
        "arabic_audio": "/static/audio/ana_b5eir_ar.mp3",
        "english_audio": "/static/audio/ana_b5eir_en.mp3",
    },
    "ana t3ban": {
        "arabic": "أنا تعبان",
        "english": "I'm tired",
        "arabic_audio": "/static/audio/ana_t3ban_ar.mp3",
        "english_audio": "/static/audio/ana_t3ban_en.mp3",
    },
    "9ba7 al5eir": {
        "arabic": "صباح الخير",
        "english": "Good morning",
        "arabic_audio": "/static/audio/9ba7_al5eir_ar.mp3",
        "english_audio": "/static/audio/9ba7_al5eir_en.mp3",
    },
    "m3 alslamh": {
        "arabic": "مع السلامة",
        "english": "Goodbye",
        "arabic_audio": "/static/audio/m3_alslamh_ar.mp3",
        "english_audio": "/static/audio/m3_alslamh_en.mp3",
    },

    # ----- Extra phrases -----
    "msa2 al5eir": {
        "arabic": "مساء الخير",
        "english": "Good evening",
        "arabic_audio": "/static/audio/msa2_al5eir_ar.mp3",
        "english_audio": "/static/audio/msa2_al5eir_en.mp3",
    },
    "t9b7 3la 5eir": {
        "arabic": "تصبح على خير",
        "english": "Good night",
        "arabic_audio": "/static/audio/t9b7_3la_5eir_ar.mp3",
        "english_audio": "/static/audio/t9b7_3la_5eir_en.mp3",
    },
    "shukran": {
        "arabic": "شكرًا",
        "english": "Thank you",
        "arabic_audio": "/static/audio/shukran_ar.mp3",
        "english_audio": "/static/audio/shukran_en.mp3",
    },
    "afwan": {
        "arabic": "عفوًا",
        "english": "You're welcome",
        "arabic_audio": "/static/audio/afwan_ar.mp3",
        "english_audio": "/static/audio/afwan_en.mp3",
    },
    "la t7aty": {
        "arabic": "لا تحاتي",
        "english": "Don't worry",
        "arabic_audio": "/static/audio/la_t7aty_ar.mp3",
        "english_audio": "/static/audio/la_t7aty_en.mp3",
    },
    "waink": {
        "arabic": "وينك؟",
        "english": "Where are you?",
        "arabic_audio": "/static/audio/waink_ar.mp3",
        "english_audio": "/static/audio/waink_en.mp3",
    },
}


@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json() or {}
    original_text = data.get("text", "")

    if not original_text.strip():
        return jsonify({"error": "No text provided"}), 400

    key = normalize(original_text)
    phrase = PHRASES.get(key)

    if not phrase:
        msg_ar = "عذرًا، هذه الجملة غير موجودة في القاموس حتى الآن."
        return jsonify({
            "arabic_raw": msg_ar,
            "arabic_corrected": msg_ar,
            "translation": msg_ar,
            "english": "English translation unavailable.",
            "arabic_audio_url": None,
            "english_audio_url": None,
        })

    return jsonify({
        "arabic_raw": phrase["arabic"],
        "arabic_corrected": phrase["arabic"],
        "translation": phrase["arabic"],
        "english": phrase["english"],
        "arabic_audio_url": phrase.get("arabic_audio"),
        "english_audio_url": phrase.get("english_audio"),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
