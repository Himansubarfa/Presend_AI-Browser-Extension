# tests/annotate_fast.py
"""Fast annotator – confirms auto‑detected extra entities."""
import json
import sys

def tokenize(text):
    tokens = []
    pos = 0
    for word in text.split():
        start = text.index(word, pos)
        end = start + len(word)
        tokens.append((word, start, end))
        pos = end
    return tokens

def main():
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        samples = [json.loads(line) for line in f]

    gold = []
    for idx, s in enumerate(samples):
        print(f"\n--- Sample {idx+1}/{len(samples)} ---")
        print(s['text'])
        if s.get('detected_extra'):
            print("\nAuto‑detected extra entities:")
            for e in s['detected_extra']:
                print(f"  {e['label']}: '{s['text'][e['start']:e['end']]}'")
            ans = input("Accept all? (y/n/q to quit): ").strip().lower()
            if ans == 'q':
                break
            if ans == 'y':
                s['entities'].extend(s['detected_extra'])
                # Remove duplicates (optional)
                seen = set()
                unique = []
                for e in s['entities']:
                    key = (e['start'], e['end'], e['label'])
                    if key not in seen:
                        seen.add(key)
                        unique.append(e)
                s['entities'] = sorted(unique, key=lambda x: x['start'])
        gold.append({'text': s['text'], 'entities': s['entities']})
        # Save incrementally
        with open('data/gold_enriched.jsonl', 'w', encoding='utf-8') as out:
            for g in gold:
                out.write(json.dumps(g) + '\n')
    print(f"\nSaved {len(gold)} enriched samples.")

if __name__ == '__main__':
    main()