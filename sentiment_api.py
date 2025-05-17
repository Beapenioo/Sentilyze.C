from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
from langdetect import detect

app = FastAPI()

# CORS ayarlarını ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm originlere izin ver
    allow_credentials=True,
    allow_methods=["*"],  # Tüm metodlara izin ver
    allow_headers=["*"],  # Tüm headerlara izin ver
)

# Türkçe model ve çok dilli model yükle
tr_model = pipeline("sentiment-analysis", model="savasy/bert-base-turkish-sentiment-cased")
multilingual_model = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

# Yıldız skorunu label'a çeviren harita (çok dilli model için)
star_to_label = {
    1: "negative",
    2: "negative",
    3: "neutral",
    4: "positive",
    5: "positive"
}
# Türkçe model için label haritası
tr_label_map = {"NEGATIVE": "negative", "NEUTRAL": "neutral", "POSITIVE": "positive"}

# Nötr cümle belirteçleri
neutral_indicators = [
    "gittim", "geldim", "yaptım", "başladı", "bitti", "sürdü", "oldu",
    "went", "came", "did", "started", "ended", "lasted", "was"
]

class AnalyzeRequest(BaseModel):
    text: str
    lang: str = "en"  # lang parametresi zorunlu değil, model zaten çok dilli

def is_likely_neutral(text: str, score: float) -> bool:
    # Eğer skor düşükse ve metin nötr belirteçler içeriyorsa
    text_lower = text.lower()
    has_neutral_indicators = any(indicator in text_lower for indicator in neutral_indicators)
    return score < 0.8 and has_neutral_indicators

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        # Dil tespiti
        lang = req.lang or detect(req.text)
        if lang == "tr":
            result = tr_model(req.text)[0]
            print("DEBUG-TR:", result)
            label = tr_label_map.get(result['label'].upper(), "neutral")
            score = float(result['score'])
            
            # Nötr cümle kontrolü
            if is_likely_neutral(req.text, score):
                label = "neutral"
                score = 0.5
            
            explanation = f"Model: {result['label']} | Score: {score:.2f}"
        else:
            result = multilingual_model(req.text)[0]
            print("DEBUG-ML:", result)
            stars = int(result['label'][0])
            label = star_to_label.get(stars, "neutral")
            score = float(result['score'])
            
            # Nötr cümle kontrolü
            if is_likely_neutral(req.text, score):
                label = "neutral"
                score = 0.5
                
            explanation = f"Model: {result['label']} | Score: {score:.2f}"
        return {"label": label, "score": score, "explanation": explanation}
    except Exception as e:
        return {"label": "error", "score": 0, "explanation": str(e)}