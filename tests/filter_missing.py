# tests/filter_missing.py
"""Find samples where the detector finds extra entity types not in ground truth."""
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.detector import detect_entities

input_file = 'data/train.jsonl'
output_file = 'data/to_annotate.jsonl'

with open(input_file, 'r', encoding='utf-8') as f:
    samples = [json.loads(line) for line in f]

filtered = []
for s in samples:
    detected = detect_entities(s['text'])
    true_labels = {e['label'] for e in s['entities']}
    extra = [
        e for e in detected
        if e['label'] not in true_labels
        and e['label'] in {'LOCATION', 'ORG', 'POSTCODE', 'PINCODE'}
    ]
    if extra:
        s['detected_extra'] = extra
        filtered.append(s)

with open(output_file, 'w', encoding='utf-8') as out:
    for s in filtered:
        out.write(json.dumps(s) + '\n')

print(f'Found {len(filtered)} samples with missing entity types.')
print(f'Saved to {output_file}')