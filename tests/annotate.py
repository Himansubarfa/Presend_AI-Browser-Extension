# tests/annotate.py
"""Interactive token‑based annotation – no dependencies required."""
import json
import os
import sys
from collections import defaultdict

def tokenize(text):
    """Simple whitespace tokeniser that preserves offsets."""
    tokens = []
    pos = 0
    for word in text.split():
        start = text.index(word, pos)
        end = start + len(word)
        tokens.append((word, start, end))
        pos = end
    return tokens

def print_tokens(tokens):
    """Display tokens with their index."""
    print("\nText tokens:")
    for i, (tok, _, _) in enumerate(tokens):
        print(f"  [{i:3d}] {tok}")

def annotate_text(text, existing_entities):
    """Allow user to correct/add entity spans."""
    tokens = tokenize(text)
    print_tokens(tokens)
    print("\nCurrent entities:")
    for ent in existing_entities:
        print(f"  {ent['label']} : '{text[ent['start']:ent['end']]}'  [{ent['start']}:{ent['end']}]")

    # Build new entity list
    new_entities = []
    while True:
        cmd = input("\nCommands:\n  a <type> <token_start> <token_end>  - add entity\n  d <index>  - delete entity (by index in list above)\n  s  - save and continue\n  q  - quit without saving\n> ").strip().lower()
        if cmd == 's':
            break
        if cmd == 'q':
            return None
        parts = cmd.split()
        if parts[0] == 'a' and len(parts) >= 4:
            label = parts[1].upper()
            try:
                start_idx = int(parts[2])
                end_idx = int(parts[3])
            except ValueError:
                print("Invalid token indices.")
                continue
            if start_idx < 0 or end_idx >= len(tokens) or start_idx > end_idx:
                print("Token indices out of range.")
                continue
            # Compute character span from token start/end
            start_char = tokens[start_idx][1]
            end_char = tokens[end_idx][2]
            new_entities.append({
                'label': label,
                'start': start_char,
                'end': end_char
            })
            # Remove overlapping original entities (simple version)
            existing_entities = [e for e in existing_entities
                                 if not (e['start'] < end_char and e['end'] > start_char)]
            print(f"Added {label}: '{text[start_char:end_char]}'")
        elif parts[0] == 'd' and len(parts) >= 2:
            idx = int(parts[1])
            if 0 <= idx < len(existing_entities):
                removed = existing_entities.pop(idx)
                print(f"Removed {removed['label']}: '{text[removed['start']:removed['end']]}'")
            else:
                print("Invalid index.")
        else:
            print("Unknown command. Use: a TYPE start end, d index, s, q")
    # Merge original (remaining) and new entities
    all_entities = existing_entities + new_entities
    all_entities.sort(key=lambda e: e['start'])
    return all_entities

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'data/train.jsonl'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'data/gold_annotated.jsonl'
    
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found.")
        sys.exit(1)
    
    gold_samples = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            sample = json.loads(line)
            print("\n" + "="*70)
            print(f"Text: {sample['text']}")
            new_entities = annotate_text(sample['text'], sample.get('entities', []))
            if new_entities is None:
                print("Skipping this sample.")
                continue
            gold_samples.append({
                'text': sample['text'],
                'entities': new_entities
            })
            # Save incrementally
            with open(output_file, 'w', encoding='utf-8') as out:
                for gs in gold_samples:
                    out.write(json.dumps(gs) + '\n')
            print(f"Saved. Total gold samples so far: {len(gold_samples)}")
    
    print(f"\nGold dataset saved to {output_file} with {len(gold_samples)} samples.")

if __name__ == '__main__':
    main()