from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from langdetect import detect
import re
import emoji
from typing import Dict, List, Tuple

app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model yükleme
tr_model_name = "dbmdz/bert-base-turkish-cased"
ml_model_name = "xlm-roberta-base"

# Tokenizer ve model yükleme
tr_tokenizer = AutoTokenizer.from_pretrained(tr_model_name)
tr_model = AutoModelForSequenceClassification.from_pretrained(tr_model_name)
ml_tokenizer = AutoTokenizer.from_pretrained(ml_model_name)
ml_model = AutoModelForSequenceClassification.from_pretrained(ml_model_name)

# Nötr cümle belirteçleri
neutral_indicators = {
    "tr": ["gittim", "geldim", "yaptım", "başladı", "bitti", "sürdü", "oldu", "aldım", "koydum", "çektim", "var", "olacak", "buluştum"],
    "en": ["went", "came", "did", "started", "ended", "lasted", "was", "bought", "put", "pulled", "have", "will", "met"]
}

# Olumsuzlama kelimeleri
negation_words = {
    "tr": ["değil", "yok", "hayır", "olmaz", "istemem", "yapmam", "etmem", "hiç", "asla", "kesinlikle", "ne", "nasıl", "yok", "olmaz", "istemiyorum", "yapmıyorum", "etmiyorum"],
    "en": ["not", "no", "never", "don't", "won't", "can't", "shouldn't", "never", "neither", "nor", "none", "doesn't", "isn't", "aren't", "wasn't", "weren't"]
}

# Güçlü duygu kelimeleri ve ifadeleri
strong_sentiment_words = {
    "tr": {
        "positive": [
            "harika", "mükemmel", "muhteşem", "süper", "olağanüstü", "çok iyi", "çok güzel",
            "inanılmaz", "fevkalade", "müthiş", "kusursuz", "memnun", "başarılı", "verimli",
            "etkileyici", "göz kamaştırıcı", "büyüleyici", "şaşırtıcı", "olağanüstü", "fevkalade",
            "etkiledi", "derinden", "tavsiye", "mutlu", "sevinçli", "gururlu", "heyecanlı",
            "coşkulu", "enerjik", "canlı", "parlak", "ışıltılı", "güvenli", "huzurlu",
            "güzel anlar", "en iyi", "en güzel", "mükemmel", "harika", "muhteşem"
        ],
        "negative": [
            "berbat", "korkunç", "rezil", "felaket", "çok kötü", "iğrenç", "dehşet",
            "kötü", "kötüleşti", "başarısız", "verimsiz", "sıkıcı", "donuyor", "bitiyor",
            "şikayet", "sorun", "problem", "hata", "kötüleşti", "başarısız", "karmaşık",
            "zor", "tatsız", "soğuk", "donuk", "sıkıcı", "yorgun", "bitkin", "üzgün",
            "kızgın", "sinirli", "stresli", "endişeli", "kaygılı", "korkulu",
            "zaman kaybı", "imkansız", "kullanılamaz", "iade", "boşa", "düşük kalite"
        ]
    },
    "en": {
        "positive": [
            "amazing", "perfect", "excellent", "wonderful", "fantastic", "great", "beautiful",
            "incredible", "outstanding", "brilliant", "flawless", "satisfied", "successful", "productive",
            "impressive", "stunning", "fascinating", "surprising", "extraordinary", "exceptional",
            "moved", "deeply", "recommend", "happy", "joyful", "proud", "excited",
            "energetic", "lively", "bright", "sparkling", "confident", "peaceful",
            "best moments", "exceeded", "caring", "professional", "excellent", "wonderful"
        ],
        "negative": [
            "terrible", "awful", "horrible", "disaster", "very bad", "disgusting", "horrible",
            "bad", "worse", "failed", "unproductive", "boring", "freezing", "draining",
            "complaint", "issue", "problem", "error", "worsened", "failed", "complex",
            "difficult", "tasteless", "cold", "dull", "boring", "tired", "exhausted",
            "sad", "angry", "annoyed", "stressed", "worried", "anxious", "fearful",
            "waste of time", "impossible", "unusable", "return", "wasted", "low quality",
            "poor", "unhelpful", "dirty", "unhappy", "unsatisfied", "disappointed"
        ]
    }
}

# Duygu güçlendirici kelimeler
intensifiers = {
    "tr": ["çok", "aşırı", "son derece", "fazlasıyla", "oldukça", "gerçekten", "kesinlikle", "mutlaka",
           "inanılmaz", "müthiş", "fevkalade", "olağanüstü", "son derece", "fazlasıyla",
           "tam bir", "kesinlikle", "mutlaka", "gerçekten", "oldukça"],
    "en": ["very", "extremely", "absolutely", "incredibly", "really", "definitely", "certainly", "absolutely",
           "amazingly", "tremendously", "exceptionally", "extraordinarily", "immensely", "vastly",
           "completely", "totally", "utterly", "absolutely", "really"]
}

class AnalyzeRequest(BaseModel):
    text: str
    lang: str = "en"

def preprocess_text(text: str) -> str:
    # Emoji analizi
    text = emoji.replace_emoji(text, replace='')
    
    # Noktalama işaretleri
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def analyze_negation(text: str, lang: str) -> float:
    words = text.lower().split()
    negation_count = sum(1 for word in words if word in negation_words[lang])
    return 1.0 - (negation_count * 0.3)  # Her olumsuzlama kelimesi 0.3 puan düşürür

def analyze_strong_sentiment(text: str, lang: str) -> float:
    text_lower = text.lower()
    score = 0.0
    
    # Pozitif kelimeleri kontrol et
    for word in strong_sentiment_words[lang]["positive"]:
        if word in text_lower:
            # Güçlendirici kelime kontrolü
            for intensifier in intensifiers[lang]:
                if f"{intensifier} {word}" in text_lower:
                    score += 0.6  # Güçlendirici ile 0.6
                    break
            else:
                score += 0.5  # Normal 0.5
    
    # Negatif kelimeleri kontrol et
    for word in strong_sentiment_words[lang]["negative"]:
        if word in text_lower:
            # Güçlendirici kelime kontrolü
            for intensifier in intensifiers[lang]:
                if f"{intensifier} {word}" in text_lower:
                    score -= 0.6  # Güçlendirici ile -0.6
                    break
            else:
                score -= 0.5  # Normal -0.5
    
    return score

def is_likely_neutral(text: str, score: float, lang: str) -> bool:
    text_lower = text.lower()
    has_neutral_indicators = any(indicator in text_lower for indicator in neutral_indicators[lang])
    return score < 0.65 and has_neutral_indicators

def get_sentiment_label(score: float) -> str:
    if score >= 0.55:  # Daha düşük pozitif eşik
        return "positive"
    elif score <= 0.45:  # Daha yüksek negatif eşik
        return "negative"
    return "neutral"

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        # Metin ön işleme
        text = preprocess_text(req.text)
        
        # Dil tespiti
        lang = req.lang or detect(text)
        
        # Model seçimi ve analiz
        if lang == "tr":
            inputs = tr_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = tr_model(**inputs)
            scores = torch.softmax(outputs.logits, dim=1)
            score = float(scores[0][1])  # Positive class score
        else:
            inputs = ml_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = ml_model(**inputs)
            scores = torch.softmax(outputs.logits, dim=1)
            score = float(scores[0][1])  # Positive class score
        
        # Olumsuzlama kontrolü
        negation_score = analyze_negation(text, lang)
        
        # Güçlü duygu kelimeleri analizi
        sentiment_score = analyze_strong_sentiment(text, lang)
        
        # Final skor hesaplama
        final_score = (score * negation_score) + sentiment_score
        
        # Nötr cümle kontrolü
        if is_likely_neutral(text, final_score, lang):
            final_score = 0.5
        
        # Sonuç
        label = get_sentiment_label(final_score)
        explanation = f"Model: {label} | Score: {final_score:.2f} | Negation Impact: {negation_score:.2f} | Sentiment Impact: {sentiment_score:.2f}"
        
        return {
            "label": label,
            "score": final_score,
            "explanation": explanation
        }
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return {"label": "error", "score": 0, "explanation": str(e)}