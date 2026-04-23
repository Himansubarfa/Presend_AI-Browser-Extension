# tests/debug_detector.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.detector import detect_entities

# Test 1: Email
text1 = "My email is john.doe@example.com and phone is +91 98765 43210"
result1 = detect_entities(text1)
print("=== Test 1: Email + Phone ===")
print(f"Input: {text1}")
print(f"Entities found: {len(result1)}")
for e in result1:
    print(f"  {e['label']}: '{e['text']}' at [{e['start']}:{e['end']}]")
print()

# Test 2: Aadhaar
text2 = "Aadhaar: 1234 5678 9012"
result2 = detect_entities(text2)
print("=== Test 2: Aadhaar ===")
print(f"Input: {text2}")
print(f"Entities found: {len(result2)}")
for e in result2:
    print(f"  {e['label']}: '{e['text']}' at [{e['start']}:{e['end']}]")
print()

# Test 3: PAN + Name
text3 = "Name: Rahul Sharma, PAN: ABCDE1234F"
result3 = detect_entities(text3)
print("=== Test 3: PAN + Name ===")
print(f"Input: {text3}")
print(f"Entities found: {len(result3)}")
for e in result3:
    print(f"  {e['label']}: '{e['text']}' at [{e['start']}:{e['end']}]")