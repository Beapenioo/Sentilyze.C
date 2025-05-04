from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

en_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
tr_model = pipeline("sentiment-analysis", model="savasy/bert-base-turkish-sentiment-cased")

class TextRequest(BaseModel):
    text: str
    lang: str = "en"  # "en" veya "tr"

@app.post("/analyze")
def analyze_sentiment(req: TextRequest):
    if req.lang == "tr":
        result = tr_model(req.text)
    else:
        result = en_model(req.text)
    return {"label": result[0]['label'], "score": result[0]['score']}