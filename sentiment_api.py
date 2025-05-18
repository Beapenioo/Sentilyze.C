from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
import emoji
from typing import Dict, List, Tuple, Any
from langdetect import detect

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
TR_MODEL_NAME = "bayrameker/turkish-sentiment-modern-bert"
EN_MODEL_NAME = "finiteautomata/bertweet-base-sentiment-analysis"

# Tokenizer ve model yükleme
tr_tokenizer = AutoTokenizer.from_pretrained(TR_MODEL_NAME)
tr_model = AutoModelForSequenceClassification.from_pretrained(TR_MODEL_NAME)

en_tokenizer = AutoTokenizer.from_pretrained(EN_MODEL_NAME)
en_model = AutoModelForSequenceClassification.from_pretrained(EN_MODEL_NAME)

# Türkçe duygu kelimeleri ve ağırlıkları
POSITIVE_WORDS_TR = {
    "güzel": 1.0, "mutlu": 1.2, "harika": 1.5, "keyif": 1.0, "iyi": 0.8, "sev": 1.2, 
    "teşekkür": 1.0, "başar": 1.2, "pozitif": 1.0, "sevinç": 1.2, "hoş": 0.8, 
    "destek": 0.8, "sıcak": 0.8, "olumlu": 1.0, "tebrik": 1.0, "başarı": 1.2, 
    "memnun": 1.2, "sevgi": 1.2, "yardım": 0.8, "şanslı": 1.0, "umut": 1.0, 
    "güler": 1.0, "hoşgörü": 1.0, "rahat": 0.8, "huzur": 1.0, "lezzetli": 1.2, 
    "lezzet": 1.0, "mükemmel": 1.5, "fantastik": 1.5, "süper": 1.2, "çok iyi": 1.2, 
    "enfes": 1.5, "başarılı": 1.2, "verimli": 1.0, "etkileyici": 1.2, "göz kamaştırıcı": 1.5,
    "büyüleyici": 1.5, "şaşırtıcı": 1.2, "olağanüstü": 1.5, "fevkalade": 1.5, "etkiledi": 1.2,
    "derinden": 1.2, "tavsiye": 1.0, "sevinçli": 1.2, "gururlu": 1.2, "heyecanlı": 1.2,
    "coşkulu": 1.2, "enerjik": 1.0, "canlı": 1.0, "parlak": 1.0, "ışıltılı": 1.0,
    "güvenli": 1.0, "huzurlu": 1.0, "güzel anlar": 1.2, "en iyi": 1.5, "en güzel": 1.5,
    "tatmin": 1.0, "övgü": 1.2, "takdir": 1.2, "beğeni": 1.2, "öner": 1.0,
    "faydalı": 1.0, "kaliteli": 1.2, "profesyonel": 1.0, "uzman": 1.0, "deneyimli": 1.0
}

NEGATIVE_WORDS_TR = {
    "kötü": -1.2, "üzgün": -1.2, "mutsuz": -1.2, "berbat": -1.5, "sinir": -1.2, 
    "korkunç": -1.5, "negatif": -1.0, "moral": -1.0, "sıkıl": -1.0, "bık": -1.0, 
    "yorgun": -0.8, "hata": -1.2, "sorun": -1.2, "problem": -1.2, "bozul": -1.2, 
    "drained": -1.0, "frustrated": -1.2, "olumsuz": -1.0, "aksilik": -1.0, 
    "üzücü": -1.2, "desteksiz": -1.0, "şanssız": -1.0, "umutsuz": -1.2, 
    "ağla": -1.2, "kavga": -1.2, "kayıp": -1.0, "zor": -1.0, "başarısız": -1.2,
    "verimsiz": -1.0, "sıkıcı": -1.2, "donuyor": -1.0, "bitiyor": -1.0, "şikayet": -1.2,
    "kötüleşti": -1.2, "karmaşık": -1.0, "tatsız": -1.2, "soğuk": -1.0, "donuk": -1.0,
    "bitkin": -1.0, "kızgın": -1.2, "stresli": -1.0, "endişeli": -1.0, "kaygılı": -1.0,
    "korkulu": -1.0, "zaman kaybı": -1.2, "imkansız": -1.5, "kullanılamaz": -1.2,
    "iade": -1.0, "boşa": -1.0, "düşük kalite": -1.2, "hayal kırıklığı": -1.5,
    "pişman": -1.2, "keşke": -1.0, "keşkeler": -1.0, "mahvol": -1.5, "mahvetti": -1.5,
    "rezil": -1.5, "felaket": -1.5, "kabus": -1.5, "kötüleş": -1.2, "bozul": -1.2,
    "çök": -1.5, "çöktü": -1.5, "başarısız": -1.2, "başarısızlık": -1.2, "kayıp": -1.0
}

# Güçlendirici kelimeler
INTENSIFIERS_TR = ["çok", "aşırı", "son derece", "fazlasıyla", "oldukça", "gerçekten", 
                   "kesinlikle", "mutlaka", "inanılmaz", "müthiş", "fevkalade", 
                   "olağanüstü", "son derece", "fazlasıyla", "tam bir", "gerçekten",
                   "oldukça", "kesinlikle", "mutlaka", "gerçekten", "oldukça",
                   "aşırı", "çok fazla", "son derece", "fazlasıyla", "oldukça",
                   "gerçekten", "kesinlikle", "mutlaka", "inanılmaz", "müthiş"]

# Olumsuzlama kelimeleri
NEGATION_WORDS_TR = ["değil", "yok", "hayır", "olmaz", "istemem", "yapmam", "etmem", 
                     "hiç", "asla", "kesinlikle", "ne", "nasıl", "yok", "olmaz", 
                     "istemiyorum", "yapmıyorum", "etmiyorum", "yok", "olmaz", "istemem",
                     "yapmam", "etmem", "hiç", "asla", "kesinlikle", "ne", "nasıl",
                     "yok", "olmaz", "istemiyorum", "yapmıyorum", "etmiyorum", "yok",
                     "olmaz", "istemem", "yapmam", "etmem", "hiç", "asla", "kesinlikle"]

class AnalyzeRequest(BaseModel):
    text: str
    lang: str = "tr"

def preprocess_text(text: str) -> str:
    # Emoji analizi
    text = emoji.replace_emoji(text, replace='')
    
    # Noktalama işaretleri
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def analyze_rule_based_tr(text: str) -> Tuple[str, float]:
    text = text.lower()
    words = text.split()
    
    # Duygu skorunu hesapla
    score = 0.0
    negation_count = 0
    context_score = 0.0
    
    # Olumsuzlama kelimelerini kontrol et
    for word in words:
        if word in NEGATION_WORDS_TR:
            negation_count += 1
    
    # Duygu kelimelerini kontrol et
    for i, word in enumerate(words):
        # Pozitif kelimeler
        for pos_word, weight in POSITIVE_WORDS_TR.items():
            if pos_word in word:
                # Güçlendirici kelime kontrolü
                for intensifier in INTENSIFIERS_TR:
                    if i > 0 and words[i-1] == intensifier:
                        score += weight * 2.0  # Güçlendirici etkiyi artırdık
                        break
                else:
                    score += weight
                break
        
        # Negatif kelimeler
        for neg_word, weight in NEGATIVE_WORDS_TR.items():
            if neg_word in word:
                # Güçlendirici kelime kontrolü
                for intensifier in INTENSIFIERS_TR:
                    if i > 0 and words[i-1] == intensifier:
                        score += weight * 2.0  # Güçlendirici etkiyi artırdık
                        break
                else:
                    score += weight
                break
    
    # Bağlam analizi - Daha detaylı
    if "ama" in words or "fakat" in words or "ancak" in words or "lakin" in words:
        context_score = -0.5  # Olumsuz bağlam etkisini artırdık
    elif "ve" in words or "ile" in words or "de" in words or "da" in words:
        context_score = 0.2  # Olumlu bağlam etkisini artırdık
    
    # Olumsuzlama varsa skoru tersine çevir
    if negation_count % 2 == 1:  # Tek sayıda olumsuzlama varsa
        score = -score * 1.5  # Olumsuzlama etkisini artırdık
    
    # Bağlam skorunu ekle
    score += context_score
    
    # Skoru normalize et (-1 ile 1 arasına)
    score = max(min(score / 2.0, 1.0), -1.0)
    
    # Etiketi belirle - Eşik değerlerini yükselttik
    if score > 0.4:  # Eşik değerini yükselttik
        label = "positive"
    elif score < -0.4:  # Eşik değerini yükselttik
        label = "negative"
    else:
        label = "neutral"
    
    return label, (score + 1) / 2  # 0-1 arasına normalize et

def analyze_bert(text: str, lang: str) -> Tuple[str, float]:
    if lang == "tr":
        tokenizer = tr_tokenizer
        model = tr_model
    else:
        tokenizer = en_tokenizer
        model = en_model
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    scores = torch.softmax(outputs.logits, dim=1)
    pred = torch.argmax(scores, dim=1).item()
    
    if pred == 2:
        label = "positive"
    elif pred == 0:
        label = "negative"
    else:
        label = "neutral"
    
    score = float(scores[0][pred])
    return label, score

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        text = preprocess_text(req.text)
        words = text.split()
        
        # Metin dilini tespit et
        try:
            detected_lang = detect(text)
            if detected_lang not in ['tr', 'en']:
                detected_lang = 'tr'  # Varsayılan olarak Türkçe kullan
        except:
            detected_lang = 'tr'  # Dil tespiti başarısız olursa Türkçe kullan
        
        # Kısa metinlerde (3 kelime veya daha az) kural tabanlı analiz uygula
        if len(words) <= 3:
            if detected_lang == 'tr':
                label, score = analyze_rule_based_tr(text)
            else:
                label, score = analyze_bert(text, 'en')
            return {
                "label": label,
                "score": score,
                "explanation": f"Short text: {'Rule-based Turkish' if detected_lang == 'tr' else 'BERT English'} analysis applied.",
                "language": detected_lang
            }
        
        # Uzun metinlerde BERT analizi uygula
        label, score = analyze_bert(text, detected_lang)
        return {
            "label": label,
            "score": score,
            "explanation": f"Long text: BERT {detected_lang.upper()} analysis applied.",
            "language": detected_lang
        }
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return {"label": "error", "score": 0, "explanation": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)