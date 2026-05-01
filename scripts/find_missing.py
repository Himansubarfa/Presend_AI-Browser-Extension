# scripts/find_missing.py
import json, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.detector import detect_entities

with open("data/test.jsonl") as f:
    test = [json.loads(l) for l in f]

for idx, s in enumerate(test):
    true = { (e['start'], e['end']) for e in s['entities'] if e['label']=='ADDRESS' }
    pred = { (e['start'], e['end']) for e in detect_entities(s['text']) if e['label']=='ADDRESS' }
    missed = true - pred
    if missed:
        print(f"\n--- Sample {idx} ---")
        print(s['text'])
        print("Missed ADDRESS spans:")
        for start,end in missed:
            print(f"  '{s['text'][start:end]}'")