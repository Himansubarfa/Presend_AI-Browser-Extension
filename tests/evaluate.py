# tests/evaluate.py
"""Evaluate the current PII detection pipeline on a labelled test set."""
import json
import sys
import os
from collections import defaultdict
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.detector import detect_entities
from seqeval.metrics import classification_report, f1_score

def load_test_data(filepath: str) -> List[Dict[str, Any]]:
    """Load JSONL file with 'text' and 'entities' fields."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def entities_to_bio(text: str, entities: List[Dict]) -> List[str]:
    """Convert entity spans to BIO tagging for seqeval."""
    tags = ['O'] * len(text)
    sorted_ents = sorted(entities, key=lambda e: (e['start'], -(e['end'] - e['start'])))
    for ent in sorted_ents:
        label = ent['label']
        start = ent['start']
        end = ent['end']
        # Validate bounds
        if start < 0 or end > len(text) or start >= end:
            continue
        for i in range(start, end):
            if i == start:
                tags[i] = f'B-{label}'
            else:
                tags[i] = f'I-{label}'
    return tags

def evaluate(test_file: str):
    """Run evaluation and print classification report."""
    test_data = load_test_data(test_file)
    y_true_all = []
    y_pred_all = []
    
    errors = []
    
    print(f"Evaluating on {len(test_data)} samples...")
    for idx, item in enumerate(test_data):
        text = item['text']
        true_entities = item['entities']
        pred_entities = detect_entities(text)
        
        true_bio = entities_to_bio(text, true_entities)
        pred_bio = entities_to_bio(text, pred_entities)
        
        # Check for length mismatches
        if len(true_bio) != len(pred_bio):
            # Truncate to match
            min_len = min(len(true_bio), len(pred_bio))
            true_bio = true_bio[:min_len]
            pred_bio = pred_bio[:min_len]
            errors.append(f"Sample {idx}: length mismatch ({len(text)} chars)")
        
        y_true_all.append(true_bio)
        y_pred_all.append(pred_bio)
        
        if (idx + 1) % 100 == 0:
            print(f"Processed {idx+1} samples")
    
    if errors:
        print(f"\nWarnings ({len(errors)}):")
        for err in errors[:5]:
            print(f"  {err}")
    
    print("\n" + "=" * 60)
    print(classification_report(y_true_all, y_pred_all, digits=4))
    overall_f1 = f1_score(y_true_all, y_pred_all)
    print(f"Overall Micro F1: {overall_f1:.4f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python evaluate.py <path_to_test.jsonl>")
        sys.exit(1)
    evaluate(sys.argv[1])