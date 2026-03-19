
#!/usr/bin/env python3
"""
Integration test for the PII masking pipeline.
Run with: python test_pipeline.py
"""

import json
from backend.utils import process_text

def run_test(name, text):
    print(f"\n=== {name} ===")
    print(f"Input: {text!r}")
    result = process_text(text)
    print(f"Masked: {result['masked']!r}")
    print(f"Entities: {json.dumps(result['entities'], indent=2)}")
    if result.get("error"):
        print(f"ERROR: {result['error']}")
    return result

def main():
    tests = [
        ("Empty string", ""),
        ("None", None),
        ("Only PERSON", "Rahul Sharma"),
        ("PERSON + EMAIL", "Rahul Sharma email rahul@gmail.com"),
        ("PERSON + PHONE + EMAIL", "Rahul Sharma phone 9876543210 email rahul@gmail.com"),
        ("With punctuation", "Rahul Sharma, email: rahul@gmail.com."),
        ("Adjacent entities", "Rahul Sharma9876543210"),
        ("Multiple occurrences", "Alice and Alice both work at Acme."),
        ("Long paragraph", (
            "John Doe (john@doe.com) called 555-1234. "
            "Jane Smith's card is 4111-1111-1111-1111."
        )),
    ]

    for name, text in tests:
        run_test(name, text)

if __name__ == "__main__":
    main()