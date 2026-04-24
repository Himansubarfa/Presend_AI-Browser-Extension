# scripts/test_model.py
from transformers import pipeline

pipe = pipeline(
    "token-classification",
    model="fine-tuned-ner-model",
    tokenizer="fine-tuned-ner-model",
    aggregation_strategy="simple"
)

text = "My name is Rajesh Kumar from Mumbai, email rajesh@example.com"
print("Input:", text)
print("Entities:", pipe(text))