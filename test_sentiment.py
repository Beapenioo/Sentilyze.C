import requests
import json
from time import sleep
from collections import defaultdict

def test_sentiment(text, lang, expected_category):
    url = "http://127.0.0.1:8001/analyze"
    data = {
        "text": text,
        "lang": lang
    }
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"\nMetin: {text}")
        print(f"Dil: {lang}")
        print(f"Beklenen: {expected_category}")
        print(f"Sonuç: {json.dumps(result, indent=2, ensure_ascii=False)}")
        print("-" * 80)
        return result["label"] == expected_category
    except Exception as e:
        print(f"Hata: {str(e)}")
        return False

def read_test_sentences():
    current_category = ""
    sentences = []
    
    with open("test_sentences.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#"):
                current_category = line
            elif line:
                lang = "tr" if "Türkçe" in current_category else "en"
                expected = "positive" if "Pozitif" in current_category else "negative" if "Negatif" in current_category else "neutral"
                sentences.append((line, lang, expected))
    
    return sentences

def calculate_metrics(results):
    metrics = defaultdict(lambda: {"correct": 0, "total": 0})
    
    for lang, expected, predicted in results:
        metrics[lang]["total"] += 1
        if expected == predicted:
            metrics[lang]["correct"] += 1
    
    return metrics

def main():
    print("Duygu Analizi Testi Başlıyor...")
    print("=" * 80)
    
    sentences = read_test_sentences()
    results = []
    
    for text, lang, expected in sentences:
        is_correct = test_sentiment(text, lang, expected)
        results.append((lang, expected, "correct" if is_correct else "incorrect"))
        sleep(1)  # API'yi yormamak için 1 saniye bekle
    
    # Metrikleri hesapla
    metrics = calculate_metrics(results)
    
    print("\nDoğruluk Oranları:")
    print("=" * 80)
    for lang, data in metrics.items():
        accuracy = (data["correct"] / data["total"]) * 100
        print(f"{lang.upper()}:")
        print(f"Toplam Test: {data['total']}")
        print(f"Doğru Tahmin: {data['correct']}")
        print(f"Doğruluk Oranı: {accuracy:.2f}%")
        print("-" * 40)

if __name__ == "__main__":
    main() 