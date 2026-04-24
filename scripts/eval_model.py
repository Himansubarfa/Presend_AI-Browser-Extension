# scripts/eval_model.py
import json
from transformers import pipeline
from seqeval.metrics import classification_report

pipe = pipeline(
    "token-classification",
    model="fine-tuned-ner-model",
    tokenizer="fine-tuned-ner-model",
    aggregation_strategy="simple"
)

# Load test data
with open("data/test.jsonl", "r", encoding="utf-8") as f:
    test_samples = [json.loads(line) for line in f]

y_true, y_pred = [], []
for sample in test_samples[:500]:  # limit if many; remove later
    text = sample["text"]
    # Ground truth BIO tags
    true_bio = ["O"] * len(text)
    for e in sorted(sample["entities"], key=lambda x: x["start"]):
        label = e["label"]
        for i in range(e["start"], e["end"]):
            true_bio[i] = f"B-{label}" if i == e["start"] else f"I-{label}"

    # Predictions from transformer
    pred_bio = ["O"] * len(text)
    try:
        results = pipe(text)
    except Exception:
        results = []
    for ent in results:
        start, end = ent["start"], ent["end"]
        label = ent["entity_group"]
        for i in range(start, end):
            pred_bio[i] = f"B-{label}" if i == start else f"I-{label}"

    y_true.append(true_bio)
    y_pred.append(pred_bio)

print(classification_report(y_true, y_pred))