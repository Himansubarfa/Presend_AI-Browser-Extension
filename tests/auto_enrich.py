# tests/auto_enrich.py
"""Automatically add detected_extra entities to the ground truth (no manual input)."""
import json
import sys
import os

input_file = 'data/to_annotate.jsonl'
output_file = 'data/gold_auto.jsonl'

if not os.path.exists(input_file):
    print(f"Input file {input_file} not found. Run tests/filter_missing.py first.")
    sys.exit(1)

with open(input_file, 'r', encoding='utf-8') as f:
    samples = [json.loads(line) for line in f]

gold = []
total_added = 0
for s in samples:
    if s.get('detected_extra'):
        # Add all extra detected entities
        s['entities'].extend(s['detected_extra'])
        # Remove exact duplicates based on (start, end, label)
        seen = set()
        unique = []
        for e in s['entities']:
            key = (e['start'], e['end'], e['label'])
            if key not in seen:
                seen.add(key)
                unique.append(e)
        s['entities'] = sorted(unique, key=lambda x: x['start'])
        total_added += len(s['detected_extra'])
    gold.append({'text': s['text'], 'entities': s['entities']})

with open(output_file, 'w', encoding='utf-8') as out:
    for g in gold:
        out.write(json.dumps(g) + '\n')

print(f"Automatically enriched {len(gold)} samples, adding {total_added} total extra entities.")
print(f"Saved to {output_file}")