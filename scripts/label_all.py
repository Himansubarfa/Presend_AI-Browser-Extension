# scripts/label_all.py
import json, sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.detector import detect_entities

for filename in ["data/address_raw.jsonl", "data/more_addresses.jsonl"]:
    with open(filename) as f:
        data = [json.loads(l) for l in f]
    for d in data:
        d['entities'] = detect_entities(d['text'])
    out_name = filename.replace(".jsonl","_labeled.jsonl")
    with open(out_name,"w") as out:
        for d in data:
            out.write(json.dumps(d)+"\n")
    print(f"Labeled {len(data)} in {out_name}")