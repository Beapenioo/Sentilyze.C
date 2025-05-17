import requests
import json
import time

# Test sentences
test_cases = {
    "positive_tr": [
        "Harika bir gün geçirdim, her şey mükemmeldi.",
        "Bu film gerçekten etkileyici ve çok beğendim.",
        "Yeni projemiz çok başarılı oldu, herkes çok mutlu."
    ],
    "positive_en": [
        "I had an amazing day, everything was perfect.",
        "This movie was truly impressive and I loved it.",
        "Our new project was very successful, everyone is happy."
    ],
    "negative_tr": [
        "Bugün çok kötü bir gün geçirdim, her şey ters gitti.",
        "Bu film berbat, zaman kaybıydı.",
        "Projemiz başarısız oldu, herkes hayal kırıklığına uğradı."
    ],
    "negative_en": [
        "I had a terrible day, everything went wrong.",
            "This movie was awful, it was a waste of time.",
        "Our project failed, everyone is disappointed."
    ],
    "neutral_tr": [
        "Bugün markete gittim ve alışveriş yaptım.",
        "Film 2 saat sürdü ve bitti.",
        "Toplantı saat 3'te başladı ve 4'te bitti."
    ],
    "neutral_en": [
        "I went to the store and did some shopping.",
        "The movie lasted 2 hours and ended.",
        "The meeting started at 3 and ended at 4."
    ]
}

def test_sentiment(text, expected_category):
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"text": text},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return {
                "text": text,
                "expected": expected_category,
                "actual": result["label"],
                "score": result["score"],
                "explanation": result["explanation"]
            }
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                return {
                    "text": text,
                    "expected": expected_category,
                    "actual": "error",
                    "score": 0,
                    "explanation": f"Request failed after {max_retries} attempts: {str(e)}"
                }

def run_tests():
    results = []
    for category, sentences in test_cases.items():
        for sentence in sentences:
            expected = category.split("_")[0]  # positive, negative, or neutral
            result = test_sentiment(sentence, expected)
            results.append(result)
    
    # Print results
    print("\nTest Results:")
    print("-" * 80)
    for result in results:
        print(f"\nText: {result['text']}")
        print(f"Expected: {result['expected']}")
        print(f"Actual: {result['actual']}")
        print(f"Score: {result['score']:.2f}")
        print(f"Explanation: {result['explanation']}")
        print("-" * 80)
    
    # Calculate accuracy
    correct = sum(1 for r in results if r['expected'] == r['actual'])
    total = len(results)
    accuracy = (correct / total) * 100
    print(f"\nOverall Accuracy: {accuracy:.2f}% ({correct}/{total} correct)")

if __name__ == "__main__":
    run_tests() 