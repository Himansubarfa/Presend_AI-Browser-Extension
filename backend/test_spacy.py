# import spacy

# # Load the brain you just downloaded
# print("Loading model...")
# nlp = spacy.load("en_core_web_sm")

# # A test sentence with sensitive data
# text = "My name is Elon Musk and I work at Tesla in Texas."
# doc = nlp(text)

# print(f"\nOriginal Text: {text}\n")

# # Loop through everything SpaCy found
# for ent in doc.ents:
#     print(f"Found: '{ent.text}'")
#     print(f"  - Label: {ent.label_}")
#     print(f"  - Start: {ent.start_char}")
#     print(f"  - End: {ent.end_char}\n")



# from backend.utils import process_text

# # Test 1
# t1 = "Rahul Sharma"
# r1 = process_text(t1)
# print("Original:", r1["original"])
# print("Masked:  ", r1["masked"])
# print("Entities:", r1["entities"])
# # Expected: masked = "[NAME]", entities = [{"label": "PERSON", "start":0, "end":12}]

# # Test 2
# t2 = "Rahul Sharma email rahul@gmail.com phone 9876543210"
# r2 = process_text(t2)
# print(r2["masked"])
# # Expected: "[NAME] email [EMAIL] phone [PHONE]"

# # Test 3 – large mixed paragraph
# t3 = """John Doe (john.doe@example.com) called 555-1234 yesterday.
#         Jane Smith's card is 4111-1111-1111-1111 and her ID is 1234 5678 9012."""
# r3 = process_text(t3)
# print(r3["masked"])
# # Visually verify all entities are replaced, order preserved, no stray characters.



# final test case run 


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