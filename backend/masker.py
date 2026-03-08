# Day 6 : implementing the masker function


# def mask_text(text: str, entities: list) -> str:
#     """
#     Takes in an original string and a list of structured entities (with start/end indices).
#     Replaces the entities inside the text with a safe, generic '[REDACTED]' placeholder.
#     Operates recursively from the end to the start to ensure indices aren't shifted!
#     """
    
#     # 1. Defense: Return early if text or entities are empty
#     if not text:
#         return ""
        
#     if not entities:
#         return text  
        
#     # 2. Extract and sort the list of entities by descending start position 
#     # Sorting by 'start' reversed = True ensures we mask from right to left
#     # This prevents earlier index positions from shifting.
#     sorted_entities = sorted(entities, key=lambda e: e['start'], reverse=True)
    
#     # 3. Create a clean list string representation of the text to easily replace text parts
#     masked_text = text
    
#     for entity in sorted_entities:
        
#         start = entity['start']
#         end = entity['end']
        
#         # Replace the entity using string slicing from the back of the list to the front
#         masked_text = masked_text[:start] + "[REDACTED]" + masked_text[end:]

#     return masked_text

# # --- TESTING BLOCK ---
# if __name__ == "__main__":
    
#     print("=== DAY 6: MASKING PHASE ===\n")
    
#     test_text = "Rahul Sharma works at Google. Reach him at rahul@gmail.com"
    
#     # Let's say we detected these entities using our detector
#     detected_entities = [
#         {"label": "PERSON", "text": "Rahul Sharma", "start": 0, "end": 12},
#         {"label": "EMAIL", "text": "rahul@gmail.com", "start": 43, "end": 58}
#     ]

#     print(f"Original Text: '{test_text}'\n")
    
#     # Send it to the masking function!
#     masked_result = mask_text(test_text, detected_entities)
    
#     print(f"Masked Result: '{masked_result}'\n")

#     # Let's try some defensive checks:
#     empty_text = mask_text("", detected_entities)
#     print(f"Empty Text test: '{empty_text}'")
    
#     empty_entities = mask_text("Nothing to redact here.", [])
#     print(f"Empty Entities test: '{empty_entities}'")



# Day 6 masker function update 1 

# backend/masker.py

# # --- NEW MASKING MAP (Step 3) ---
# MASK_LABELS = {
#     "PERSON": "[NAME]",
#     "EMAIL": "[EMAIL]",
#     "PHONE": "[PHONE]",
#     "ID": "[ID]",
#     "CARD": "[CARD]"
# }

# def mask_text(text: str, entities: list) -> str:
#     """
#     Takes in an original string and a list of structured entities.
#     Returns a new string with the entities safely replaced using MASK_LABELS.
#     Operates recursively from the end to the start to ensure indices aren't shifted!
#     """
#     if not text:
#         return ""
        
#     if not entities:
#         return text  
        
#     sorted_entities = sorted(entities, key=lambda e: e['start'], reverse=True)
    
#     masked_text = text
    
#     for entity in sorted_entities:
#         start = entity['start']
#         end = entity['end']
#         label = entity['label']
        
#         # --- NEW LOGIC: Use Map or Default ---
#         # Fetch the correct replacement tag based on the label.
#         # If we see a new label we haven't mapped yet, we default to [REDACTED].
#         replacement_text = MASK_LABELS.get(label, "[REDACTED]")
        
#         masked_text = masked_text[:start] + replacement_text + masked_text[end:]

#     return masked_text

# # --- TESTING BLOCK ---
# if __name__ == "__main__":
#     print("=== DAY 6: MASKING PHASE TEST (Step 3) ===\n")
    
#     test_text = "Rahul Sharma works at Google. Reach him at rahul@gmail.com. His ID is 1234-5678-9012"
    
#     detected_entities = [
#         {"label": "PERSON", "text": "Rahul Sharma", "start": 0, "end": 12},
#         {"label": "EMAIL", "text": "rahul@gmail.com", "start": 43, "end": 58},
#         {"label": "ID", "text": "1234-5678-9012", "start": 70, "end": 84}
#     ]

#     print(f"Original Text: '{test_text}'\n")
#     masked_result = mask_text(test_text, detected_entities)
#     print(f"Masked Result: '{masked_result}'\n")



# Day 6 : update 2 

# backend/masker.py

# # --- MASKING MAP (Step 3) ---
# MASK_LABELS = {
#     "PERSON": "[NAME]",
#     "EMAIL": "[EMAIL]",
#     "PHONE": "[PHONE]",
#     "ID": "[ID]",
#     "CARD": "[CARD]"
# }

# # --- END TO START REPLACEMENT LOGIC (Step 4) ---
# def mask_text(text: str, entities: list) -> str:
#     """
#     Takes an original string and a list of entities.
#     Returns a string where the entities are safely replaced.
#     Operates recursively from the end to the start to ensure indices aren't shifted.
#     """
#     # 1. Defense: Handle empty text or entities safely
#     if not text:
#         return ""
        
#     if not entities:
#         return text  
        
#     # 2. Sort the entities by start position descending (Right-to-Left!)
#     # This prevents earlier index positions from shifting.
#     sorted_entities = sorted(entities, key=lambda e: e['start'], reverse=True)
    
#     masked_text = text
    
#     # 3. Replace each entity
#     for entity in sorted_entities:
#         start = entity['start']
#         end = entity['end']
#         label = entity['label']
        
#         # Use MASK_LABELS mapping, default to "[REDACTED]" if label isn't found
#         replacement_text = MASK_LABELS.get(label, "[REDACTED]")
        
#         # Slicing from start to finish
#         masked_text = masked_text[:start] + replacement_text + masked_text[end:]

#     return masked_text

# # --- TESTING BLOCK ---
# if __name__ == "__main__":
#     print("=== DAY 6: MASKING PHASE TEST (Step 4) ===\n")
    
#     test_text = "Rahul Sharma works at Google. Reach him at rahul@gmail.com. His ID is 1234-5678-9012"
    
#     # Simulating data our detector might produce:
#     detected_entities = [
#         {"label": "PERSON", "text": "Rahul Sharma", "start": 0, "end": 12},
#         {"label": "EMAIL", "text": "rahul@gmail.com", "start": 43, "end": 58},
#         {"label": "ID", "text": "1234-5678-9012", "start": 70, "end": 84}
#     ]

#     print(f"Original Text: '{test_text}'\n")
#     masked_result = mask_text(test_text, detected_entities)
#     print(f"Masked Result: '{masked_result}'\n")



# Day 6 :update 3 


# # backend/masker.py

# # --- MASKING MAP (Step 3) ---
# MASK_LABELS = {
#     "PERSON": "[NAME]",
#     "EMAIL": "[EMAIL]",
#     "PHONE": "[PHONE]",
#     "ID": "[ID]",
#     "CARD": "[CARD]"
# }

# # --- END TO START REPLACEMENT LOGIC (Step 4) ---
# def mask_text(text: str, entities: list) -> str:
#     """
#     Takes an original string and a list of entities.
#     Returns a string where the entities are safely replaced.
#     Operates recursively from the end to the start to ensure indices aren't shifted.
#     """
#     if not text:
#         return ""
        
#     if not entities:
#         return text  
        
#     sorted_entities = sorted(entities, key=lambda e: e['start'], reverse=True)
    
#     masked_text = text
    
#     for entity in sorted_entities:
#         start = entity['start']
#         end = entity['end']
#         label = entity['label']
        
#         replacement_text = MASK_LABELS.get(label, "[REDACTED]")
#         masked_text = masked_text[:start] + replacement_text + masked_text[end:]

#     return masked_text

# # --- TESTING BLOCK (Step 5) ---
# if __name__ == "__main__":
#     print("=== DAY 6: MASKING PHASE TEST (Step 5) ===\n")
    
#     # --- Test 1 ---
#     test_1 = "Rahul Sharma"
#     entities_1 = [{"label": "PERSON", "start": 0, "end": 12}]
    
#     # --- Test 2 ---
#     test_2 = "Rahul Sharma email rahul@gmail.com"
#     entities_2 = [
#         {"label": "PERSON", "start": 0, "end": 12},
#         {"label": "EMAIL", "start": 19, "end": 34}
#     ]
    
#     # --- Test 3 ---
#     test_3 = "Rahul Sharma phone 9876543210 email rahul@gmail.com"
#     entities_3 = [
#         {"label": "PERSON", "start": 0, "end": 12},
#         {"label": "PHONE", "start": 19, "end": 29},
#         {"label": "EMAIL", "start": 36, "end": 51}
#     ]

#     print("--- Test 1 ---")
#     print(f"Original: '{test_1}'")
#     print(f"Masked:   '{mask_text(test_1, entities_1)}'\n")

#     print("--- Test 2 ---")
#     print(f"Original: '{test_2}'")
#     print(f"Masked:   '{mask_text(test_2, entities_2)}'\n")

#     print("--- Test 3 ---")
#     print(f"Original: '{test_3}'")
#     print(f"Masked:   '{mask_text(test_3, entities_3)}'\n")



# DAY 6 : UPDATE 4 

# backend/masker.py
# backend/masker.py

# --- MASKING MAP (Step 3) ---
# MASK_LABELS = {
#     "PERSON": "[NAME]",
#     "EMAIL": "[EMAIL]",
#     "PHONE": "[PHONE]",
#     "ID": "[ID]",
#     "CARD": "[CARD]"
# }

# # --- END TO START REPLACEMENT LOGIC (Step 4) + DOUBLE MASKING SAFEGUARD (Step 6) ---
# def mask_text(text: str, entities: list) -> str:
#     """
#     Takes an original string and a list of entities.
#     Returns a string where the entities are safely replaced.
#     Operates from the end to the start to ensure indices aren't shifted.
#     Skips replacement if the target slice is already the intended mask label
#     (prevents double masking).
#     """
#     if not text:
#         return ""
#     if not entities:
#         return text

#     # Sort entities by start index descending (process from end to start)
#     sorted_entities = sorted(entities, key=lambda e: e['start'], reverse=True)
#     masked_text = text

#     for entity in sorted_entities:
#         start = entity['start']
#         end = entity['end']
#         label = entity['label']
#         replacement_text = MASK_LABELS.get(label, "[REDACTED]")

#         # ----- Step 6 safeguard: skip if already masked -----
#         if masked_text[start:end] == replacement_text:
#             continue

#         masked_text = masked_text[:start] + replacement_text + masked_text[end:]

#     return masked_text

# # --- TESTING BLOCK (Steps 5 & 6) ---
# if __name__ == "__main__":
#     print("=== DAY 6: MASKING PHASE TEST (Steps 5 & 6) ===\n")

#     # --- Test 1: Single PERSON ---
#     test_1 = "Rahul Sharma"
#     entities_1 = [{"label": "PERSON", "start": 0, "end": 12}]

#     # --- Test 2: PERSON + EMAIL ---
#     test_2 = "Rahul Sharma email rahul@gmail.com"
#     entities_2 = [
#         {"label": "PERSON", "start": 0, "end": 12},
#         {"label": "EMAIL", "start": 19, "end": 34}
#     ]

#     # --- Test 3: PERSON + PHONE + EMAIL ---
#     test_3 = "Rahul Sharma phone 9876543210 email rahul@gmail.com"
#     entities_3 = [
#         {"label": "PERSON", "start": 0, "end": 12},
#         {"label": "PHONE", "start": 19, "end": 29},
#         {"label": "EMAIL", "start": 36, "end": 51}
#     ]

#     # --- Test 4: Literal mask already present (double masking prevention) ---
#     # Suppose the text already contains "[NAME]" as literal text,
#     # and an entity (e.g., from a faulty NER) covers that exact span.
#     test_4 = "Hello [NAME]"
#     entities_4 = [{"label": "PERSON", "start": 6, "end": 12}]   # points to "[NAME]"

#     # --- Test 5: Double application with same valid entities (simulates accidental recall) ---
#     # First, mask a normal string to get a masked version.
#     original = "Contact Rahul at rahul@example.com"
#     entities_5 = [
#         {"label": "PERSON", "start": 8, "end": 13},
#         {"label": "EMAIL", "start": 17, "end": 34}
#     ]
#     first_pass = mask_text(original, entities_5)
#     # Now apply the *same* entities again (which are now stale) – this should NOT produce
#     # double masking because the indices are invalid, but the safeguard won't help here.
#     # We include this to show that the safeguard is not designed for stale indices,
#     # and that users must avoid reusing old entity lists.
#     second_pass = mask_text(first_pass, entities_5)

#     print("--- Test 1 ---")
#     print(f"Original: '{test_1}'")
#     print(f"Masked:   '{mask_text(test_1, entities_1)}'\n")

#     print("--- Test 2 ---")
#     print(f"Original: '{test_2}'")
#     print(f"Masked:   '{mask_text(test_2, entities_2)}'\n")

#     print("--- Test 3 ---")
#     print(f"Original: '{test_3}'")
#     print(f"Masked:   '{mask_text(test_3, entities_3)}'\n")

#     print("--- Test 4 (literal mask already present) ---")
#     print(f"Original: '{test_4}'")
#     print(f"Masked:   '{mask_text(test_4, entities_4)}' (should be identical)\n")

#     print("--- Test 5 (double application with stale entities) ---")
#     print(f"Original: '{original}'")
#     print(f"After first mask:  '{first_pass}'")
#     print(f"After second mask (stale entities): '{second_pass}'")
#     print("(The second result is garbled because indices are no longer valid  safeguard cannot fix misuse.)\n")



# Day 6 final update 

# backend/masker.py

# # ====================== MASKING MAP (Step 3) ======================
# MASK_LABELS = {
#     "PERSON": "[NAME]",
#     "EMAIL": "[EMAIL]",
#     "PHONE": "[PHONE]",
#     "ID": "[ID]",
#     "CARD": "[CARD]"
# }

# # ====================== MASKING FUNCTION (Steps 4 & 6) ======================
# def mask_text(text: str, entities: list) -> str:
#     """
#     Replaces entity spans in the text with corresponding mask labels.

#     Args:
#         text (str): Original text.
#         entities (list): List of entity dicts with keys: label, start, end.

#     Returns:
#         str: Text with entities replaced.
#     """
#     if not text or not entities:
#         return text

#     # Process from the end to avoid index shifts
#     sorted_entities = sorted(entities, key=lambda e: e['start'], reverse=True)
#     masked = text

#     for ent in sorted_entities:
#         start, end, label = ent['start'], ent['end'], ent['label']
#         replacement = MASK_LABELS.get(label, "[REDACTED]")

#         # Step 6 safeguard: skip if already masked (prevents double masking)
#         if masked[start:end] == replacement:
#             continue

#         masked = masked[:start] + replacement + masked[end:]

#     return masked

# # ====================== TESTING BLOCK (Steps 5, 7, 8) ======================
# if __name__ == "__main__":
#     print("=== DAY 6: MASKING PHASE TEST (Steps 5–8) ===\n")

#     # ----- Step 5: Basic tests (already verified) -----
#     print("--- Step 5: Basic masking ---")
#     test1 = "Rahul Sharma"
#     ent1 = [{"label": "PERSON", "start": 0, "end": 12}]
#     print(f"'{test1}' → '{mask_text(test1, ent1)}'")

#     test2 = "Rahul Sharma email rahul@gmail.com"
#     ent2 = [
#         {"label": "PERSON", "start": 0, "end": 12},
#         {"label": "EMAIL", "start": 19, "end": 34}   # corrected end index
#     ]
#     print(f"'{test2}' → '{mask_text(test2, ent2)}'")

#     test3 = "Rahul Sharma phone 9876543210 email rahul@gmail.com"
#     ent3 = [
#         {"label": "PERSON", "start": 0, "end": 12},
#         {"label": "PHONE", "start": 19, "end": 29},
#         {"label": "EMAIL", "start": 36, "end": 51}
#     ]
#     print(f"'{test3}' → '{mask_text(test3, ent3)}'\n")

#     # ----- Step 6: Double‑masking prevention (already verified) -----
#     print("--- Step 6: Double‑masking prevention ---")
#     test4 = "Hello [NAME]"
#     ent4 = [{"label": "PERSON", "start": 6, "end": 12}]   # covers the literal [NAME]
#     result4 = mask_text(test4, ent4)
#     print(f"'{test4}' → '{result4}' (should be identical)\n")

#     # ----- Step 7: Preserve surrounding punctuation and spaces -----
#     print("--- Step 7: Preserve punctuation and spaces ---")
#     test_punct = "Rahul Sharma, email: rahul@gmail.com."
#     # indices:
#     # "Rahul Sharma" -> 0-12
#     # ", email: " -> 12-21
#     # "rahul@gmail.com" -> 21-36? Actually let's compute:
#     # "Rahul Sharma, email: rahul@gmail.com."
#     # 0         12         21        36       37 (period)
#     # "Rahul Sharma" (0-12)
#     # ", email: " (12-21)
#     # "rahul@gmail.com" (21-36)
#     # "." (36-37)
#     ent_punct = [
#         {"label": "PERSON", "start": 0, "end": 12},
#         {"label": "EMAIL", "start": 21, "end": 36}
#     ]
#     result_punct = mask_text(test_punct, ent_punct)
#     expected_punct = "[NAME], email: [EMAIL]."
#     print(f"Original: '{test_punct}'")
#     print(f"Masked:   '{result_punct}'")
#     print(f"Expected: '{expected_punct}'")
#     print("✅ Punctuation preserved\n" if result_punct == expected_punct else "❌ Mismatch\n")

#     # ----- Step 8: Stress tests -----
#     print("--- Step 8: Stress tests ---")

#     # 8.1 Adjacent entities
#     test_adjacent = "Rahul Sharma9876543210"
#     # PERSON: 0-12, PHONE: 12-22 (since "9876543210" is 10 digits)
#     ent_adjacent = [
#         {"label": "PERSON", "start": 0, "end": 12},
#         {"label": "PHONE", "start": 12, "end": 22}
#     ]
#     result_adjacent = mask_text(test_adjacent, ent_adjacent)
#     print("Adjacent entities:")
#     print(f"'{test_adjacent}' → '{result_adjacent}' (expected '[NAME][PHONE]')")

#     # 8.2 Long paragraph with multiple occurrences and punctuation
#     long_para = (
#         "John Doe met Jane Doe at the conference. "
#         "John's email is john@doe.com, and Jane's email is jane@doe.com. "
#         "Call John at 555-1234 or Jane at 555-5678."
#     )
#     # Entities (simplified for demo – in practice they'd come from a detector)
#     ent_long = [
#         {"label": "PERSON", "start": 0, "end": 8},    # John Doe
#         {"label": "PERSON", "start": 13, "end": 21},  # Jane Doe
#         {"label": "PERSON", "start": 41, "end": 45},  # John
#         {"label": "EMAIL", "start": 57, "end": 70},   # john@doe.com
#         {"label": "PERSON", "start": 76, "end": 80},  # Jane
#         {"label": "EMAIL", "start": 91, "end": 104},  # jane@doe.com
#         {"label": "PERSON", "start": 112, "end": 116},# John
#         {"label": "PHONE", "start": 121, "end": 129}, # 555-1234
#         {"label": "PERSON", "start": 134, "end": 138},# Jane
#         {"label": "PHONE", "start": 143, "end": 151}, # 555-5678
#     ]
#     result_long = mask_text(long_para, ent_long)
#     print("\nLong paragraph with multiple entities:")
#     print(result_long)

#     # 8.3 Repeated same entity type
#     test_repeat = "Alice and Alice both work at Acme."
#     ent_repeat = [
#         {"label": "PERSON", "start": 0, "end": 5},    # Alice
#         {"label": "PERSON", "start": 10, "end": 15},  # Alice
#     ]
#     result_repeat = mask_text(test_repeat, ent_repeat)
#     print("\nRepeated entities:")
#     print(f"'{test_repeat}' → '{result_repeat}'")

#     # 8.4 Random spacing (extra spaces)
#     test_spacing = "  Bob   Smith  called  555-1212  ."
#     # Indices carefully counted: let's compute approximate
#     # We'll assume detector gives spans ignoring extra spaces? Actually spaces are part of text.
#     # For demonstration, we manually set spans that include the names and phone.
#     # "  Bob   Smith  called  555-1212  ."
#     # indices: 0-2 spaces, 2-5 "Bob", 5-8 spaces, 8-13 "Smith", 13-15 spaces, 15-21 "called", 21-23 spaces, 23-31 "555-1212", 31-33 spaces, 33-34 "."
#     ent_spacing = [
#         {"label": "PERSON", "start": 2, "end": 5},    # Bob
#         {"label": "PERSON", "start": 8, "end": 13},   # Smith
#         {"label": "PHONE", "start": 23, "end": 31},   # 555-1212
#     ]
#     result_spacing = mask_text(test_spacing, ent_spacing)
#     print("\nRandom spacing:")
#     print(f"'{test_spacing}' → '{result_spacing}'")

#     print("\n✅ All stress tests executed (visually verify correctness).")

# # ====================== END OF FILE ======================





# final code 1 


# """
# PII masking module.
# Maps entity labels to placeholder strings and safely replaces spans in text.
# """

# import logging
# from typing import List, Dict, Any

# logger = logging.getLogger(__name__)

# # ====================== MASKING MAP ======================
# MASK_LABELS = {
#     "PERSON": "[NAME]",
#     "EMAIL": "[EMAIL]",
#     "PHONE": "[PHONE]",
#     "ID": "[ID]",
#     "CARD": "[CARD]"
# }

# # ====================== MASKING FUNCTION ======================
# def mask_text(text: str, entities: List[Dict[str, Any]]) -> str:
#     """
#     Replaces entity spans in the text with corresponding mask labels.

#     Args:
#         text (str): Original text.
#         entities (list): List of entity dicts with keys: label, start, end.

#     Returns:
#         str: Text with entities replaced.

#     Raises:
#         ValueError: If any entity has invalid indices.
#     """
#     if not text:
#         return text
#     if not entities:
#         return text

#     # Validate entities and ensure indices are within bounds
#     text_len = len(text)
#     for idx, ent in enumerate(entities):
#         if not all(k in ent for k in ('label', 'start', 'end')):
#             raise ValueError(f"Entity {idx} missing required keys: {ent}")
#         if not isinstance(ent['start'], int) or not isinstance(ent['end'], int):
#             raise ValueError(f"Entity {idx} start/end must be integers: {ent}")
#         if ent['start'] < 0 or ent['end'] > text_len or ent['start'] >= ent['end']:
#             raise ValueError(f"Entity {idx} has invalid span ({ent['start']}:{ent['end']}) for text of length {text_len}")

#     # Process from the end to avoid index shifts
#     sorted_entities = sorted(entities, key=lambda e: e['start'], reverse=True)
#     masked = text

#     for ent in sorted_entities:
#         start, end, label = ent['start'], ent['end'], ent['label']
#         replacement = MASK_LABELS.get(label, "[REDACTED]")

#         # Safeguard: skip if already masked (prevents double masking)
#         if masked[start:end] == replacement:
#             logger.debug("Skipping already masked span at %d:%d", start, end)
#             continue

#         masked = masked[:start] + replacement + masked[end:]

#     return masked


# # (Optional) Remove the test block for production, or keep it for standalone testing.
# # If you keep it, consider moving it to a separate test file.
# if __name__ == "__main__":
#     # This block is for development/testing only.
#     # In production, use proper unit tests.
#     print("=== MASKER TEST ===\n")
#     # ... (you can keep your existing tests here)



# final code for prodcution ready 


"""
PII masking module.
Maps entity labels to placeholder strings and safely replaces spans in text.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Mapping from entity label to mask placeholder
MASK_LABELS = {
    "PERSON": "[NAME]",
    "EMAIL": "[EMAIL]",
    "PHONE": "[PHONE]",
    "ID": "[ID]",
    "CARD": "[CARD]",
    "ADDRESS": "[ADDRESS]",
    "ORG": "[ORG]"
}


def mask_text(text: str, entities: List[Dict[str, Any]]) -> str:
    """
    Replaces entity spans in the text with corresponding mask labels.

    Args:
        text (str): Original text.
        entities (list): List of entity dicts with keys: label, start, end.

    Returns:
        str: Text with entities replaced.

    Raises:
        ValueError: If any entity has invalid indices.
    """
    if not text:
        return text
    if not entities:
        return text

    # Validate entities and ensure indices are within bounds
    text_len = len(text)
    for idx, ent in enumerate(entities):
        if not all(k in ent for k in ('label', 'start', 'end')):
            raise ValueError(f"Entity {idx} missing required keys: {ent}")
        if not isinstance(ent['start'], int) or not isinstance(ent['end'], int):
            raise ValueError(f"Entity {idx} start/end must be integers: {ent}")
        if ent['start'] < 0 or ent['end'] > text_len or ent['start'] >= ent['end']:
            raise ValueError(f"Entity {idx} has invalid span ({ent['start']}:{ent['end']}) for text of length {text_len}")

    # Process from the end to avoid index shifts
    sorted_entities = sorted(entities, key=lambda e: e['start'], reverse=True)
    masked = text

    for ent in sorted_entities:
        start, end, label = ent['start'], ent['end'], ent['label']
        replacement = MASK_LABELS.get(label, "[REDACTED]")

        # Safeguard: skip if already masked (prevents double masking)
        if masked[start:end] == replacement:
            logger.debug("Skipping already masked span at %d:%d", start, end)
            continue

        masked = masked[:start] + replacement + masked[end:]

    return masked