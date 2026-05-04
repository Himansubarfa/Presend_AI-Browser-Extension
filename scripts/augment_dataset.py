# scripts/augment_dataset.py
import json, random, os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.detector import detect_entities

def augment_text(text):
    # Randomly insert line breaks, extra spaces, punctuation noise
    text = text.replace("\n", random.choice(["\n\n", "\n", " "]))
    if random.random() < 0.3:
        text = text.replace(",", " ,").replace(".", " .")
    # Insert random missing characters? No, keep it realistic.
    return text

with open("data/train.jsonl", encoding="utf-8") as f:
    original = [json.loads(l) for l in f]

augmented = []
for s in original:
    for _ in range(2):  # 2x augmentation
        new_text = augment_text(s["text"])
        ents = detect_entities(new_text)
        if ents:
            augmented.append({"text": new_text, "entities": ents})

with open("data/augmented_train.jsonl", "w", encoding="utf-8") as f:
    for item in original + augmented:
        f.write(json.dumps(item) + "\n")
print(f"Augmented dataset size: {len(original)+len(augmented)}")