# scripts/label_address_data.py
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.detector import detect_entities

with open('data/address_raw.jsonl', 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f]

for d in data:
    d['entities'] = detect_entities(d['text'])

with open('data/address_labeled.jsonl', 'w', encoding='utf-8') as out:
    for d in data:
        out.write(json.dumps(d) + '\n')

print(f'Labeled {len(data)} address samples.')