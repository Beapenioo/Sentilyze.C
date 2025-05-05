from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

class AnalyzeRequest(BaseModel):
    text: str
    lang: str

POSITIVE_WORDS_TR = [
    "güzel", "mutlu", "harika", "keyif", "iyi", "sev", "teşekkür", "başar", "pozitif", "sevinç", "hoş", "destek", "sıcak", "olumlu", "tebrik", "başarı", "memnun", "sevgi", "yardım", "şanslı", "umut", "güler", "hoşgörü", "rahat", "huzur"
]
NEGATIVE_WORDS_TR = [
    "kötü", "üzgün", "mutsuz", "berbat", "sinir", "korkunç", "negatif", "moral", "sıkıl", "bık", "yorgun", "hata", "sorun", "problem", "bozul", "drained", "frustrated", "olumsuz", "aksilik", "üzücü", "desteksiz", "şanssız", "umutsuz", "ağla", "kavga", "kayıp", "zor"
]
POSITIVE_WORDS_EN = [
    "happy", "good", "great", "wonderful", "enjoy", "positive", "success", "love", "excellent", "amazing", "pleased", "delighted", "laugh", "smile", "support", "warm", "congratulations", "achievement", "succeed", "helpful"
]
NEGATIVE_WORDS_EN = [
    "bad", "sad", "angry", "terrible", "awful", "negative", "problem", "issue", "fail", "hate", "frustrated", "tired", "drained", "upset", "disappointed", "unhappy", "worse", "worry", "trouble", "unlucky", "unfortunate"
]

def stem_tr(word):
    for ek in ["lar", "ler", "im", "ım", "um", "üm", "sin", "sın", "sun", "sün", "yim", "yım", "yum", "yüm", "muz", "mız", "miz", "müz", "nız", "niz", "nuz", "nüz", "dan", "den", "ta", "te", "da", "de", "li", "lu", "lü", "lı", "ca", "ce", "çi", "çı", "cu", "cü", "sız", "siz", "suz", "süz", "lik", "lık", "luk", "lük", "ci", "cı", "cu", "cü"]:
        if word.endswith(ek):
            return word[:-len(ek)]
    return word

def count_matches_tr(words, text):
    count = 0
    kelimeler = re.findall(r'\b\w+\b', text)
    matched = []
    for kelime in kelimeler:
        kok = stem_tr(kelime)
        for word in words:
            if word in kok or kok in word:
                count += 1
                matched.append((kelime, kok, word))
                break
    print(f"[DEBUG] Türkçe kök eşleşmeleri: {matched}")
    return count

def count_matches_en(words, text):
    count = 0
    for word in words:
        if re.search(r'\b' + re.escape(word) + r'\b', text):
            count += 1
        elif word in text:
            count += 1
    return count

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    text = req.text.lower()
    lang = req.lang.lower()
    pos_count = neg_count = 0

    if lang == "tr":
        pos_count = count_matches_tr(POSITIVE_WORDS_TR, text)
        neg_count = count_matches_tr(NEGATIVE_WORDS_TR, text)
        print(f"[DEBUG] Pozitif eşleşme sayısı: {pos_count}, Negatif eşleşme sayısı: {neg_count}")
    else:
        pos_count = count_matches_en(POSITIVE_WORDS_EN, text)
        neg_count = count_matches_en(NEGATIVE_WORDS_EN, text)

    if pos_count > neg_count:
        label = "positive"
        score = min(0.6 + 0.1 * pos_count, 1.0)
        explanation = "The text expresses positive sentiment." if lang == "en" else "Metin olumlu duygular içeriyor."
    elif neg_count > pos_count:
        label = "negative"
        score = min(0.6 + 0.1 * neg_count, 1.0)
        explanation = "The text expresses negative sentiment." if lang == "en" else "Metin olumsuz duygular içeriyor."
    else:
        label = "neutral"
        score = 0.5
        explanation = "The text expresses neutral sentiment." if lang == "en" else "Metin nötr duygular içeriyor."

    return {"label": label, "score": score, "explanation": explanation}