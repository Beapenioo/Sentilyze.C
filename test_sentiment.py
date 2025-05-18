import requests
import json
from time import sleep
from collections import defaultdict

def test_sentiment(text: str, expected_category: str, lang: str = "tr") -> bool:
    try:
        response = requests.post(
            "http://127.0.0.1:8002/analyze",
            json={"text": text, "lang": lang}
        )
        if response.status_code == 200:
            result = response.json()
            predicted_label = result["label"]
            score = result["score"]
            explanation = result["explanation"]
            
            print(f"\nCümle: {text}")
            print(f"Beklenen: {expected_category}")
            print(f"Sonuç: {predicted_label} (Skor: {score:.2f})")
            print(f"Açıklama: {explanation}")
            
            return predicted_label == expected_category
        else:
            print(f"Hata: {response.status_code} - {response.text}")
            return False
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
    
    for lang, expected, result in results:
        metrics[lang]["total"] += 1
        if result == "correct":  # Eğer beklenen kategori ile tahmin edilen kategori aynıysa
            metrics[lang]["correct"] += 1
    
    return metrics

def main():
    print("Duygu Analizi Testi Başlıyor...")
    print("=" * 80)
    
    sentences = read_test_sentences()
    results = []
    correct_count = 0
    total_count = 0
    
    for text, lang, expected in sentences:
        is_correct = test_sentiment(text, expected, lang)
        results.append((lang, expected, "correct" if is_correct else "incorrect"))
        if is_correct:
            correct_count += 1
        total_count += 1
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
    
    # Toplam doğruluk oranı
    print(f"\nGenel Sonuçlar:")
    print(f"Toplam Test: {total_count}")
    print(f"Toplam Doğru Tahmin: {correct_count}")
    print(f"Genel Doğruluk Oranı: {(correct_count/total_count)*100:.2f}%")

if __name__ == "__main__":
    main() 