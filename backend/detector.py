# Day 2 implementation

# import spacy

# # 1. Start with an empty global variable
# nlp = None

# def detect_entities(text: str) -> list:
#     """
#     Analyzes text and extracts only PERSON entities.
#     Uses lazy loading for the NLP model.
#     """
#     global nlp # Tell Python we want to use the global variable
    
#     # 2. Lazy Initialization Pattern
#     # Only load the model if it hasn't been loaded yet!
#     if nlp is None:
#         print("Loading spaCy model into memory for the first time...")
#         nlp = spacy.load("en_core_web_sm")
    
#     # Run the text through the spaCy pipeline
#     doc = nlp(text)
    
#     detected_persons = []
    
#     # Loop through all found entities
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             detected_persons.append({
#                 "label": ent.label_,
#                 "text": ent.text,
#                 "start": ent.start_char,
#                 "end": ent.end_char
#             })
            
#     return detected_persons

# # --- Testing Block ---
# # if __name__ == "__main__":
# #     test_text_1 = "Rahul Sharma went to Microsoft."
# #     test_text_2 = "Satya Nadella is the CEO."
    
# #     print("--- First Call ---")
# #     print(detect_entities(test_text_1)) # You will see the loading print statement here
    
# #     print("\n--- Second Call ---")
# #     print(detect_entities(test_text_2)) # You will NOT see the loading print statement here!

# # --- Testing Block1 ---
# # if __name__ == "__main__":
# #     # The exact example input from your guide
# #     test_text = "Rahul Sharma works at Microsoft."
    
# #     print(f"Input: {test_text}\n")
# #     print("Detected Entities:")
# #     print("-" * 20)
    
# #     # Run the detector
# #     results = detect_entities(test_text)
    
# #     # Print the clean formatted output
# #     for entity in results:
# #         print(f"{entity['text']} → {entity['label']}")



# # --- Testing Block 3 ---
# if __name__ == "__main__":
#     # A list of our edge case test sentences
#     test_cases = [
#         "Hello world",
#         "Rahul Sharma met Ankit Verma.",
#         "My name is Rahul Sharma and I live in Bangalore."
#     ]

#     # Loop through each test case
#     for i, text in enumerate(test_cases, 1):
#         print(f"\nTest {i}: '{text}'")
#         print("-" * 40)
        
#         # Run the detector
#         results = detect_entities(text)
        
#         # Check if the list is empty
#         if len(results) == 0:
#             print("Result: [] (No PERSON entities found)")
#         else:
#             # Print the detailed breakdown for each entity found
#             for entity in results:
#                 print(f"{entity['text']} → {entity['label']}")
#                 print(f"  - Start position: {entity['start']}")
#                 print(f"  - End position: {entity['end']}")




# # The final detector.py 
# import spacy

# # Global variable for lazy loading
# nlp = None

# def detect_entities(text: str) -> list:
#     """
#     Analyzes the input text and extracts PERSON entities.
    
#     Args:
#         text (str): The raw string text to be analyzed.
        
#     Returns:
#         list: A list of dictionaries, each containing the 'label', 
#               'text', 'start', and 'end' positions of the detected entity.
#     """
#     # 1. Handle empty text safely right at the start
#     if not text:
#         return []
        
#     global nlp
    
#     # 2. Lazy Initialization
#     if nlp is None:
#         print("Loading spaCy model into memory for the first time...")
#         nlp = spacy.load("en_core_web_sm")
    
#     # 3. Process the text
#     doc = nlp(text)
#     detected_persons = []
    
#     # 4. Extract entities
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             detected_persons.append({
#                 "label": ent.label_,
#                 "text": ent.text,
#                 "start": ent.start_char,
#                 "end": ent.end_char
#             })
            
#     return detected_persons

# # --- Testing Block ---
# if __name__ == "__main__":
#     test_cases = [
#         "",                     # Testing the new empty text safeguard
#         "Hello world",          # No entities
#         "Rahul Sharma met Ankit Verma.", # Multiple entities
#         "My name is Rahul Sharma and I live in Bangalore." # Mixed entities
#     ]

#     for i, text in enumerate(test_cases, 1):
#         print(f"\nTest {i}: '{text}'")
#         print("-" * 40)
        
#         results = detect_entities(text)
        
#         if not results:
#             print("Result: [] (No PERSON entities found or empty text)")
#         else:
#             for entity in results:
#                 print(f"{entity['text']} → {entity['label']} (Start: {entity['start']}, End: {entity['end']})")




# Day 3 Implementation

# Day 3 : Adding the Email-detection
# import spacy
# import re

# # Global variable for lazy loading
# nlp = None

# def detect_entities(text: str) -> list:
#     """
#     Analyzes the input text and extracts PERSON entities using AI (spaCy).
#     """
#     if not text:
#         return []
        
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model into memory for the first time...")
#         nlp = spacy.load("en_core_web_sm")
    
#     doc = nlp(text)
#     detected_persons = []
    
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             detected_persons.append({
#                 "label": ent.label_,
#                 "text": ent.text,
#                 "start": ent.start_char,
#                 "end": ent.end_char
#             })
            
#     return detected_persons

# def detect_emails(text: str) -> list:
#     """
#     Analyzes text and extracts EMAIL entities using Regular Expressions.
#     """
#     if not text:
#         return []
        
#     detected_emails = []
#     # The robust regex pattern from your guide
#     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    
#     # re.finditer loops through every match it finds in the text
#     for match in re.finditer(email_pattern, text):
#         detected_emails.append({
#             "label": "EMAIL",
#             "text": match.group(),
#             "start": match.start(),
#             "end": match.end()
#         })
        
#     return detected_emails

# # --- Testing Block ---
# if __name__ == "__main__":
#     print("--- Testing Email Detection Edge Cases ---")
    
#     # The exact test cases from your guide
#     email_test_cases = [
#         "Reach out to rahul@gmail.com for details.",
#         "My work address is test.user@domain.co.in",
#         "This is an invalid@ address that should not match."
#     ]

#     for i, text in enumerate(email_test_cases, 1):
#         print(f"\nTest {i}: '{text}'")
#         print("-" * 40)
        
#         results = detect_emails(text)
        
#         if not results:
#             print("Result: [] (No EMAIL entities found)")
#         else:
#             for entity in results:
#                 print(f"{entity['text']} → {entity['label']} (Start: {entity['start']}, End: {entity['end']})")




# Day 3 : part 2 adding phone number detection 
# import spacy
# import re

# # Global variable for lazy loading
# nlp = None

# def detect_entities(text: str) -> list:
#     """Analyzes text and extracts PERSON entities using AI (spaCy)."""
#     if not text: return []
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model into memory for the first time...")
#         nlp = spacy.load("en_core_web_sm")
    
#     doc = nlp(text)
#     detected_persons = []
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             detected_persons.append({
#                 "label": ent.label_, "text": ent.text,
#                 "start": ent.start_char, "end": ent.end_char
#             })
#     return detected_persons

# def detect_emails(text: str) -> list:
#     """Analyzes text and extracts EMAIL entities using Regex."""
#     if not text: return []
#     detected_emails = []
#     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    
#     for match in re.finditer(email_pattern, text):
#         detected_emails.append({
#             "label": "EMAIL", "text": match.group(),
#             "start": match.start(), "end": match.end()
#         })
#     return detected_emails

# def detect_phones(text: str) -> list:
#     """Analyzes text and extracts PHONE entities using Regex."""
#     if not text: return []
#     detected_phones = []
    
#     # Upgraded regex to handle the hyphen/space in the middle of the number
#     phone_pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
    
#     for match in re.finditer(phone_pattern, text):
#         detected_phones.append({
#             "label": "PHONE",
#             "text": match.group(),
#             "start": match.start(),
#             "end": match.end()
#         })
        
#     return detected_phones

# # --- Testing Block ---
# if __name__ == "__main__":
#     print("--- Testing Phone Detection ---")
    
#     # The exact test cases from your guide, plus a random long number edge case
#     phone_test_cases = [
#         "Call me at 9876543210 tomorrow.",
#         "My international number is +91 9876543210.",
#         "Try the formatted number: 98765-43210.",
#         "Order ID 123456789012345 should not match as phone."
#     ]

#     for i, text in enumerate(phone_test_cases, 1):
#         print(f"\nTest {i}: '{text}'")
#         print("-" * 40)
        
#         results = detect_phones(text)
        
#         if not results:
#             print("Result: [] (No PHONE entities found)")
#         else:
#             for entity in results:
#                 print(f"{entity['text']} → {entity['label']} (Start: {entity['start']}, End: {entity['end']})")


# Day 3 : adding the Adhaar Number detection


# import spacy
# import re

# # Global variable for lazy loading
# nlp = None

# def detect_entities(text: str) -> list:
#     """Analyzes text and extracts PERSON entities using AI (spaCy)."""
#     if not text: return []
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model into memory for the first time...")
#         nlp = spacy.load("en_core_web_sm")
    
#     doc = nlp(text)
#     detected_persons = []
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             detected_persons.append({
#                 "label": ent.label_, "text": ent.text,
#                 "start": ent.start_char, "end": ent.end_char
#             })
#     return detected_persons

# def detect_emails(text: str) -> list:
#     """Analyzes text and extracts EMAIL entities using Regex."""
#     if not text: return []
#     detected_emails = []
#     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     for match in re.finditer(email_pattern, text):
#         detected_emails.append({
#             "label": "EMAIL", "text": match.group(),
#             "start": match.start(), "end": match.end()
#         })
#     return detected_emails

# def detect_phones(text: str) -> list:
#     """Analyzes text and extracts PHONE entities using Regex."""
#     if not text: return []
#     detected_phones = []
#     phone_pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     for match in re.finditer(phone_pattern, text):
#         detected_phones.append({
#             "label": "PHONE", "text": match.group(),
#             "start": match.start(), "end": match.end()
#         })
#     return detected_phones

# def detect_ids(text: str) -> list:
#     """Analyzes text and extracts Aadhaar/ID entities using Regex."""
#     if not text: return []
#     detected_ids = []
    
#     # The regex pattern for 12-digit Aadhaar formats
#     id_pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    
#     for match in re.finditer(id_pattern, text):
#         detected_ids.append({
#             "label": "ID",
#             "text": match.group(),
#             "start": match.start(),
#             "end": match.end()
#         })
        
#     return detected_ids

# # --- Testing Block ---
# if __name__ == "__main__":
#     print("--- Testing ID/Aadhaar Detection ---")
    
#     # The exact test cases from your guide
#     id_test_cases = [
#         "Here is my ID: 1234 5678 9012.",
#         "Unformatted ID: 123456789012.",
#         "Hyphenated ID: 1234-5678-9012.",
#         "invalid 1111 2222 (partial)"
#     ]

#     for i, text in enumerate(id_test_cases, 1):
#         print(f"\nTest {i}: '{text}'")
#         print("-" * 40)
        
#         results = detect_ids(text)
        
#         if not results:
#             print("Result: [] (No ID entities found)")
#         else:
#             for entity in results:
#                 print(f"{entity['text']} → {entity['label']} (Start: {entity['start']}, End: {entity['end']})")



# Day 3 : adding the credit card detection 

# import spacy
# import re

# # Global variable for lazy loading
# nlp = None

# def detect_entities(text: str) -> list:
#     """Analyzes text and extracts PERSON entities using AI (spaCy)."""
#     if not text: return []
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model into memory for the first time...")
#         nlp = spacy.load("en_core_web_sm")
    
#     doc = nlp(text)
#     detected_persons = []
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             detected_persons.append({
#                 "label": ent.label_, "text": ent.text,
#                 "start": ent.start_char, "end": ent.end_char
#             })
#     return detected_persons

# def detect_emails(text: str) -> list:
#     """Analyzes text and extracts EMAIL entities using Regex."""
#     if not text: return []
#     detected_emails = []
#     email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     for match in re.finditer(email_pattern, text):
#         detected_emails.append({
#             "label": "EMAIL", "text": match.group(),
#             "start": match.start(), "end": match.end()
#         })
#     return detected_emails

# def detect_phones(text: str) -> list:
#     """Analyzes text and extracts PHONE entities using Regex."""
#     if not text: return []
#     detected_phones = []
#     phone_pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     for match in re.finditer(phone_pattern, text):
#         detected_phones.append({
#             "label": "PHONE", "text": match.group(),
#             "start": match.start(), "end": match.end()
#         })
#     return detected_phones

# def detect_ids(text: str) -> list:
#     """Analyzes text and extracts Aadhaar/ID entities using Regex."""
#     if not text: return []
#     detected_ids = []
#     id_pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(id_pattern, text):
#         detected_ids.append({
#             "label": "ID", "text": match.group(),
#             "start": match.start(), "end": match.end()
#         })
#     return detected_ids

# def detect_cards(text: str) -> list:
#     """Analyzes text and extracts Credit Card entities using Regex."""
#     if not text: return []
#     detected_cards = []
    
#     # Regex pattern for 16-digit credit card formats
#     card_pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    
#     for match in re.finditer(card_pattern, text):
#         detected_cards.append({
#             "label": "CARD",
#             "text": match.group(),
#             "start": match.start(),
#             "end": match.end()
#         })
        
#     return detected_cards

# # --- Testing Block ---
# if __name__ == "__main__":
#     print("--- Testing Credit Card Detection ---")
    
#     # Test cases for Credit Cards
#     card_test_cases = [
#         "My card number is 4532 1234 5678 9010.",
#         "Unformatted card: 4532123456789010.",
#         "Hyphenated card: 4532-1234-5678-9010.",
#         "Short number 4532 1234 5678 (should not match)"
#     ]

#     for i, text in enumerate(card_test_cases, 1):
#         print(f"\nTest {i}: '{text}'")
#         print("-" * 40)
        
#         results = detect_cards(text)
        
#         if not results:
#             print("Result: [] (No CARD entities found)")
#         else:
#             for entity in results:
#                 print(f"{entity['text']} → {entity['label']} (Start: {entity['start']}, End: {entity['end']})")



# Day 3 :Integration of  spacy and regex entities 


# import spacy
# import re

# # Global variable for lazy loading
# nlp = None

# def detect_emails(text: str) -> list:
#     """Extracts EMAIL entities using Regex."""
#     if not text: return []
#     detected = []
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "EMAIL", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_phones(text: str) -> list:
#     """Extracts PHONE entities using Regex."""
#     if not text: return []
#     detected = []
#     pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "PHONE", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_ids(text: str) -> list:
#     """Extracts Aadhaar/ID entities using Regex."""
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "ID", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_cards(text: str) -> list:
#     """Extracts Credit Card entities using Regex."""
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "CARD", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_entities(text: str) -> list:
#     """
#     Analyzes text and extracts ALL entities (AI + Regex).
#     Returns a unified list sorted by the start position.
#     """
#     if not text: return []
    
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model into memory for the first time...\n")
#         nlp = spacy.load("en_core_web_sm")
    
#     all_entities = []
    
#     # 1. Run spaCy (AI) for PERSON
#     doc = nlp(text)
#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             all_entities.append({
#                 "label": ent.label_, "text": ent.text,
#                 "start": ent.start_char, "end": ent.end_char
#             })
            
#     # 2. Run Regex (Deterministic Rules) for everything else
#     # The .extend() method adds the items from one list into another
#     all_entities.extend(detect_emails(text))
#     all_entities.extend(detect_phones(text))
#     all_entities.extend(detect_ids(text))
#     all_entities.extend(detect_cards(text))
    
#     # 3. Sort the unified list by the 'start' character position (ascending)
#     # This lambda function tells Python: "Sort this list based on the 'start' dictionary key"
#     all_entities.sort(key=lambda x: x['start'])
    
#     return all_entities

# # # --- Testing Block 1 ---
# # if __name__ == "__main__":
# #     print("--- Final Day 3 Integration Test ---")
    
# #     # The ultimate test case with one of everything!
# #     master_test = "Rahul Sharma can be reached at rahul@gmail.com or 9876543210. His ID is 1234 5678 9012 and card is 4532 1234 5678 9010."
    
# #     print(f"Input Text: '{master_test}'")
# #     print("-" * 60)
    
# #     results = detect_entities(master_test)
    
# #     import json
# #     # Print it out in beautiful, readable JSON format
# #     print(json.dumps(results, indent=4))


# # --- Testing Block 2 ---


# # --- Testing Block ---
# if __name__ == "__main__":
#     print("--- Day 3 Final Combined Test ---")
    
#     # The exact test string from your guide
#     test_text = "Rahul Sharma email rahul@gmail.com phone 9876543210 Aadhaar 1234 5678 9012"
    
#     print(f"Input Text: '{test_text}'")
#     print("-" * 60)
    
#     # Run the combined detector
#     results = detect_entities(test_text)
    
#     import json
#     # Print the output in a clean, readable format
#     print(json.dumps(results, indent=4))





# Day 3 final final implementation


# import spacy
# import re

# # --- GLOBAL VARIABLES ---
# # This is the line that was missing and caused your error!
# nlp = None

# # --- REGEX HELPER FUNCTIONS ---
# def detect_emails(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "EMAIL", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_phones(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "PHONE", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_ids(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "ID", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_cards(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "CARD", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# # --- MAIN ORCHESTRATOR FUNCTION ---
# def detect_entities(text: str) -> list:
#     """
#     Analyzes text and extracts ALL entities safely.
#     Includes empty text guards, crash prevention, and deduplication.
#     """
#     # Safety Check 1: Handle empty or invalid text safely
#     if not text or not isinstance(text, str):
#         return []
    
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model into memory for the first time...")
#         nlp = spacy.load("en_core_web_sm")
    
#     all_entities = []
    
#     # Safety Check 2: Prevent crashes using a try/except block
#     try:
#         # 1. Run spaCy (AI)
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 all_entities.append({
#                     "label": ent.label_, "text": ent.text,
#                     "start": ent.start_char, "end": ent.end_char
#                 })
                
#         # 2. Run Regex
#         all_entities.extend(detect_emails(text))
#         all_entities.extend(detect_phones(text))
#         all_entities.extend(detect_ids(text))
#         all_entities.extend(detect_cards(text))
        
#     except Exception as e:
#         print(f"Warning: Detection encountered an error - {e}")
#         return []

#     # Safety Check 3: Remove duplicate spans
#     unique_entities = []
#     seen_spans = set()
    
#     for entity in all_entities:
#         span = (entity['start'], entity['end'])
#         if span not in seen_spans:
#             seen_spans.add(span)
#             unique_entities.append(entity)
            
#     # 4. Sort by start position
#     unique_entities.sort(key=lambda x: x['start'])
    
#     return unique_entities

# # --- TESTING BLOCK ---
# if __name__ == "__main__":
#     print("--- Day 3 Final Safety Check Test ---")
    
#     safety_tests = [
#         "",
#         "Rahul Sharma at rahul@gmail.com",
#         None  # Testing the invalid type check
#     ]
    
#     for i, test in enumerate(safety_tests, 1):
#         print(f"\nTest {i} Input: '{test}'")
#         results = detect_entities(test)
#         print(f"Output: {results}")




# DAY 4 : optimising the model 

# day 4 update 1 


# import spacy
# import re

# # --- GLOBAL VARIABLES ---
# # This is the line that was missing and caused your error!
# nlp = None

# # --- REGEX HELPER FUNCTIONS ---
# def detect_emails(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "EMAIL", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_phones(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "PHONE", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_ids(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "ID", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_cards(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "CARD", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# # --- MAIN ORCHESTRATOR FUNCTION ---
# def detect_entities(text: str) -> list:
#     """
#     Analyzes text and extracts ALL entities safely.
#     Includes empty text guards, crash prevention, and deduplication.
#     """
#     # Safety Check 1: Handle empty or invalid text safely
#     if not text or not isinstance(text, str):
#         return []
    
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model into memory for the first time...")
#         nlp = spacy.load("en_core_web_sm")
    
#     all_entities = []
    
#     # Safety Check 2: Prevent crashes using a try/except block
#     try:
#         # 1. Run spaCy (AI)
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 all_entities.append({
#                     "label": ent.label_, "text": ent.text,
#                     "start": ent.start_char, "end": ent.end_char
#                 })
                
#         # 2. Run Regex
#         all_entities.extend(detect_emails(text))
#         all_entities.extend(detect_phones(text))
#         all_entities.extend(detect_ids(text))
#         all_entities.extend(detect_cards(text))
        
#     except Exception as e:
#         print(f"Warning: Detection encountered an error - {e}")
#         return []

#     # Safety Check 3: Remove duplicate spans
#     unique_entities = []
#     seen_spans = set()
    
#     for entity in all_entities:
#         span = (entity['start'], entity['end'])
#         if span not in seen_spans:
#             seen_spans.add(span)
#             unique_entities.append(entity)
            
#     # 4. Sort by start position
    
#     # 4. Sort by start ascending, then length descending
#     unique_entities.sort(key=lambda x: (x['start'], -(x['end'] - x['start'])))

#     return unique_entities

# # --- TESTING BLOCK ---
# if __name__ == "__main__":
#     print("--- Day 3 Final Safety Check Test ---")
    
#     safety_tests = [
#         "",
#         "Rahul Sharma at rahul@gmail.com",
#         None  # Testing the invalid type check
#     ]
    
#     for i, test in enumerate(safety_tests, 1):
#         print(f"\nTest {i} Input: '{test}'")
#         results = detect_entities(test)
#         print(f"Output: {results}")



# Day 4  update 2


# import spacy
# import re

# nlp = None

# # --- REGEX HELPER FUNCTIONS ---
# def detect_emails(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "EMAIL", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_phones(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "PHONE", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_ids(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "ID", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_cards(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "CARD", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# # --- NEW: THE OVERLAP REFEREE ---
# def resolve_overlaps(spans: list) -> list:
#     """
#     Takes a list of entity spans, resolves any overlaps by keeping the longest span,
#     and returns a clean, conflict-free list.
#     """
#     if not spans:
#         return []

#     # Ensure they are perfectly sorted (Step 2 logic)
#     # 1st priority: start position (ascending)
#     # 2nd priority: length (descending) -> we use negative length to sort descending
#     sorted_spans = sorted(spans, key=lambda x: (x['start'], -(x['end'] - x['start'])))
    
#     clean_spans = []
    
#     for span in sorted_spans:
#         # If our clean list is empty, just add the first item
#         if not clean_spans:
#             clean_spans.append(span)
#         else:
#             # Look at the last span we approved
#             last_span = clean_spans[-1]
            
#             # Check for overlap: does the current span start BEFORE the last one ends?
#             if span['start'] < last_span['end']:
#                 # OVERLAP DETECTED! Find out which one is longer
#                 last_length = last_span['end'] - last_span['start']
#                 current_length = span['end'] - span['start']
                
#                 if current_length > last_length:
#                     # The new one is longer, so it replaces the old one
#                     clean_spans[-1] = span
#                 # If the new one is shorter or equal, we do nothing (ignore it)
                
#             else:
#                 # No overlap! Safe to add to the clean list
#                 clean_spans.append(span)
                
#     return clean_spans

# # --- MAIN ORCHESTRATOR FUNCTION ---
# def detect_entities(text: str) -> list:
#     if not text or not isinstance(text, str):
#         return []
    
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model...")
#         nlp = spacy.load("en_core_web_sm")
    
#     all_entities = []
    
#     try:
#         # 1. AI Detection
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 all_entities.append({
#                     "label": ent.label_, "text": ent.text,
#                     "start": ent.start_char, "end": ent.end_char
#                 })
                
#         # 2. Regex Detection
#         all_entities.extend(detect_emails(text))
#         all_entities.extend(detect_phones(text))
#         all_entities.extend(detect_ids(text))
#         all_entities.extend(detect_cards(text))
        
#     except Exception as e:
#         print(f"Warning: Detection encountered an error - {e}")
#         return []

#     # 3. Run the overlaps referee to get the final clean list!
#     final_clean_entities = resolve_overlaps(all_entities)
    
#     return final_clean_entities

# # --- TESTING BLOCK ---
# if __name__ == "__main__":
#     print("--- Day 4 Overlap Resolution Test ---")
    
#     # This text has a massive conflict! 
#     # "1234 5678 9010" is 12 digits (ID) inside "4532 1234 5678 9010" (16 digit CARD)
#     conflict_test = "My ID might be 1234 5678 9010, but my card is 4532 1234 5678 9010."
    
#     print(f"Input: '{conflict_test}'")
#     results = detect_entities(conflict_test)
    
#     import json
#     print(json.dumps(results, indent=4))




# Day 4 update 3 


# import spacy

# import re

# nlp = None

# # --- REGEX HELPER FUNCTIONS ---
# def detect_emails(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "EMAIL", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_phones(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "PHONE", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_ids(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "ID", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_cards(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "CARD", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# # --- NEW: THE OVERLAP REFEREE ---
# # --- THE PRIORITY MAP ---
# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ID": 3,
#     "CARD": 2,
#     "PERSON": 1
# }

# # --- THE OVERLAP REFEREE ---
# def resolve_overlaps(spans: list) -> list:
#     """
#     Resolves overlaps by keeping the longest span.
#     In the event of a tie, keeps the span with the higher priority label.
#     """
#     if not spans:
#         return []

#     # THE MAGIC SORTING RULE:
#     # 1. Start position (ascending) -> x['start']
#     # 2. Length (descending) -> -(x['end'] - x['start'])
#     # 3. Priority (descending) -> -PRIORITY_MAP.get(x['label'], 0)
#     sorted_spans = sorted(
#         spans, 
#         key=lambda x: (
#             x['start'], 
#             -(x['end'] - x['start']), 
#             -PRIORITY_MAP.get(x['label'], 0)
#         )
#     )
    
#     clean_spans = []
    
#     for span in sorted_spans:
#         if not clean_spans:
#             clean_spans.append(span)
#         else:
#             last_span = clean_spans[-1]
            
#             # Check for overlap
#             if span['start'] < last_span['end']:
#                 last_length = last_span['end'] - last_span['start']
#                 current_length = span['end'] - span['start']
                
#                 # Because we pre-sorted by priority, if lengths are equal, 
#                 # the one already in clean_spans is guaranteed to be the higher priority!
#                 # We only need to replace it if the new one is strictly LONGER.
#                 if current_length > last_length:
#                     clean_spans[-1] = span
#             else:
#                 clean_spans.append(span)
                
#     return clean_spans

# # --- MAIN ORCHESTRATOR FUNCTION ---
# def detect_entities(text: str) -> list:
#     if not text or not isinstance(text, str):
#         return []
    
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model...")
#         nlp = spacy.load("en_core_web_sm")
    
#     all_entities = []
    
#     try:
#         # 1. AI Detection
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 all_entities.append({
#                     "label": ent.label_, "text": ent.text,
#                     "start": ent.start_char, "end": ent.end_char
#                 })
                
#         # 2. Regex Detection
#         all_entities.extend(detect_emails(text))
#         all_entities.extend(detect_phones(text))
#         all_entities.extend(detect_ids(text))
#         all_entities.extend(detect_cards(text))
        
#     except Exception as e:
#         print(f"Warning: Detection encountered an error - {e}")
#         return []

#     # 3. Run the overlaps referee to get the final clean list!
#     final_clean_entities = resolve_overlaps(all_entities)
    
#     return final_clean_entities

# # --- TESTING BLOCK ---
# # if __name__ == "__main__":
# #     print("--- Day 4 Overlap Resolution Test ---")
    
# #     # This text has a massive conflict! 
# #     # "1234 5678 9010" is 12 digits (ID) inside "4532 1234 5678 9010" (16 digit CARD)
# #     conflict_test = "My ID might be 1234 5678 9010, but my card is 4532 1234 5678 9010."
    
# #     print(f"Input: '{conflict_test}'")
# #     results = detect_entities(conflict_test)
    
# #     import json
# #     print(json.dumps(results, indent=4))
# # --- TESTING BLOCK ---
# # if __name__ == "__main__":
# #     print("--- Day 4 Priority Conflict Test ---")
    
# #     # We will manually create a fake conflict where spaCy and Regex 
# #     # both claim the exact same 15 characters (0 to 15).
# #     fake_conflict_spans = [
# #         {"label": "PERSON", "text": "rahul@gmail.com", "start": 0, "end": 15},
# #         {"label": "EMAIL", "text": "rahul@gmail.com", "start": 0, "end": 15}
# #     ]
    
# #     print("Incoming Messy Spans:")
# #     for span in fake_conflict_spans:
# #         print(f" - {span['label']}")
        
# #     # Send it to the referee!
# #     results = resolve_overlaps(fake_conflict_spans)
    
# #     import json
# #     print("\nWinning Span After Referee:")
# #     print(json.dumps(results, indent=4))

# # --- TESTING BLOCK ---
# if __name__ == "__main__":
#     import json
#     print("--- Day 4 Official Overlap Tests ---\n")
    
#     # Test 1: The ID vs CARD Overlap
#     # A 16-digit number will trigger the ID regex (first 12) AND the CARD regex (all 16).
#     test_1 = "My number is 4532 1234 5678 9010."
#     print("Test 1: ID vs CARD Overlap")
#     print(f"Input: '{test_1}'")
#     print(json.dumps(detect_entities(test_1), indent=2))
#     print("-" * 40)
    
#     # Test 2: Standard non-overlapping sentence
#     test_2 = "Rahul Sharma email rahul@gmail.com"
#     print("Test 2: Normal Sentence")
#     print(f"Input: '{test_2}'")
#     print(json.dumps(detect_entities(test_2), indent=2))
#     print("-" * 40)
    
#     # Test 3: Manual Overlap
#     # Pretend spaCy thought "Apple" was a person, but another rule knew "Apple Inc" was an ORG.
#     manual_spans = [
#         {"label": "PERSON", "text": "Apple", "start": 0, "end": 5},
#         {"label": "ORG", "text": "Apple Inc", "start": 0, "end": 9}
#     ]
#     print("Test 3: Manual Overlap Check")
#     print("Incoming Messy Spans:")
#     print(json.dumps(manual_spans, indent=2))
#     print("Referee Output (Cleaned):")
#     print(json.dumps(resolve_overlaps(manual_spans), indent=2))
#     print("-" * 40)
    
#     # Test 4: Repeated Entity
#     # The text is identical, but they live at different character coordinates!
#     test_4 = "Rahul Sharma called Rahul Sharma."
#     print("Test 4: Repeated Entity")
#     print(f"Input: '{test_4}'")
#     print(json.dumps(detect_entities(test_4), indent=2))
#     print("-" * 40)



# Day 4 final update 

# import spacy
# import re

# # --- GLOBALS & CONFIG ---
# nlp = None

# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ID": 3,
#     "CARD": 2,
#     "PERSON": 1
# }

# # --- 1. REGEX DETECTORS ---
# def detect_emails(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "EMAIL", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_phones(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "PHONE", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_ids(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "ID", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_cards(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "CARD", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# # --- 2. OVERLAP REFEREE ---
# def resolve_overlaps(spans: list) -> list:
#     """
#     Sorts spans and resolves overlaps by keeping the longest span.
#     Uses PRIORITY_MAP as a tiebreaker for spans of exact equal length and position.
#     """
#     if not spans:
#         return []

#     # Sort by: 1. Start (Left-to-Right), 2. Length (Longest First), 3. Priority (Highest First)
#     sorted_spans = sorted(
#         spans, 
#         key=lambda x: (
#             x['start'], 
#             -(x['end'] - x['start']), 
#             -PRIORITY_MAP.get(x['label'], 0)
#         )
#     )
    
#     clean_spans = []
    
#     for span in sorted_spans:
#         if not clean_spans:
#             clean_spans.append(span)
#         else:
#             last_span = clean_spans[-1]
            
#             # If current span starts before the last one ends, it's an overlap!
#             if span['start'] < last_span['end']:
#                 last_length = last_span['end'] - last_span['start']
#                 current_length = span['end'] - span['start']
                
#                 # Only replace if the new overlapping span is strictly LONGER
#                 if current_length > last_length:
#                     clean_spans[-1] = span
#             else:
#                 # No overlap, safe to add
#                 clean_spans.append(span)
                
#     return clean_spans

# # --- 3. MAIN ORCHESTRATOR ---
# def detect_entities(text: str) -> list:
#     """
#     Master function: Runs AI and Regex, merges results, resolves conflicts, 
#     and returns a perfectly clean list of entities to redact.
#     """
#     if not text or not isinstance(text, str):
#         return []
    
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model...")
#         nlp = spacy.load("en_core_web_sm")
    
#     all_entities = []
    
#     try:
#         # Step A: Get spaCy spans (AI)
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 all_entities.append({
#                     "label": ent.label_, "text": ent.text,
#                     "start": ent.start_char, "end": ent.end_char
#                 })
                
#         # Step B: Get Regex spans (Rules)
#         all_entities.extend(detect_emails(text))
#         all_entities.extend(detect_phones(text))
#         all_entities.extend(detect_ids(text))
#         all_entities.extend(detect_cards(text))
        
#     except Exception as e:
#         print(f"Warning: Detection encountered an error - {e}")
#         return []

#     # Step C: Merge, resolve overlaps, and return final list
#     final_clean_entities = resolve_overlaps(all_entities)
#     return final_clean_entities

# # --- TESTING BLOCK 1 ---
# # if __name__ == "__main__":
# #     import json
# #     print("--- Day 4 Final Refactor Test ---\n")
# #     test_text = "Rahul Sharma's email is rahul@gmail.com and his card is 4532 1234 5678 9010."
# #     print(f"Analyzing: '{test_text}'\n")
# #     print(json.dumps(detect_entities(test_text), indent=2))


# # --- TESTING BLOCK 2 ---
# # --- TESTING BLOCK ---
# if __name__ == "__main__":
#     print("--- Day 4 Final Determinism Test ---\n")
    
#     test_text = "Rahul Sharma works at Google. Reach him at rahul@gmail.com or 9876543210. ID: 1234 5678 9012, Card: 4532 1234 5678 9010."
    
#     print(f"Testing Input: '{test_text}'\n")
    
#     # Run the first baseline test
#     baseline_result = detect_entities(test_text)
#     print("Run 1: baseline established.")
    
#     is_deterministic = True
    
#     # Run it 4 more times and compare it to the baseline
#     for i in range(2, 6):
#         current_result = detect_entities(test_text)
        
#         # Check if this run perfectly matches the first run
#         if current_result == baseline_result:
#             print(f"Run {i}: PERFECT MATCH")
#         else:
#             print(f"Run {i}: FAILED! Output was different.")
#             is_deterministic = False
            
#     print("-" * 40)
#     if is_deterministic:
#         print("✅ SUCCESS: Your detection engine is 100% deterministic!")
#     else:
#         print("❌ ERROR: Randomness detected in the pipeline.")



# Day 5 step 2,3,4 are combined


# import spacy
# import re

# nlp = None

# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ID": 3,
#     "CARD": 2,
#     "PERSON": 1
# }

# # --- 1. NORMALIZATION LAYER (DAY 5) ---
# def normalize_text(text: str) -> str:
#     """
#     Cleans messy input text to prevent AI crashes and standardize spacing.
#     Converts None to empty string, strips edges, and flattens multiple spaces/tabs.
#     """
#     if text is None or not isinstance(text, str):
#         return ""
    
#     # Strip leading/trailing whitespace
#     text = text.strip()
    
#     # Replace multiple spaces, tabs (\t), or newlines (\n) with a single space
#     text = re.sub(r'\s+', ' ', text)
    
#     return text

# # --- 2. REGEX DETECTORS (Updated with IGNORECASE) ---
# def detect_emails(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     # Added re.IGNORECASE to catch RAHUL@GMAIL.COM
#     for match in re.finditer(pattern, text, flags=re.IGNORECASE):
#         detected.append({"label": "EMAIL", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_phones(text: str) -> list:
#     if not text: return []
#     detected = []
#     # \b ensures we don't grab numbers hiding inside letters (Step 4)
#     pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "PHONE", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_ids(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "ID", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_cards(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "CARD", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# # --- 3. OVERLAP REFEREE ---
# def resolve_overlaps(spans: list) -> list:
#     if not spans: return []

#     sorted_spans = sorted(
#         spans, 
#         key=lambda x: (x['start'], -(x['end'] - x['start']), -PRIORITY_MAP.get(x['label'], 0))
#     )
    
#     clean_spans = []
#     for span in sorted_spans:
#         if not clean_spans:
#             clean_spans.append(span)
#         else:
#             last_span = clean_spans[-1]
#             if span['start'] < last_span['end']:
#                 last_length = last_span['end'] - last_span['start']
#                 current_length = span['end'] - span['start']
#                 if current_length > last_length:
#                     clean_spans[-1] = span
#             else:
#                 clean_spans.append(span)
                
#     return clean_spans

# # --- 4. MAIN ORCHESTRATOR ---
# def detect_entities(text: str) -> list:
#     # 1. Run the text through the new Normalization Layer first!
#     clean_text = normalize_text(text)
    
#     if not clean_text:
#         return []
    
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model...")
#         nlp = spacy.load("en_core_web_sm")
    
#     all_entities = []
    
#     try:
#         # Pass the CLEANED text to the detectors
#         doc = nlp(clean_text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 all_entities.append({
#                     "label": ent.label_, "text": ent.text,
#                     "start": ent.start_char, "end": ent.end_char
#                 })
                
#         all_entities.extend(detect_emails(clean_text))
#         all_entities.extend(detect_phones(clean_text))
#         all_entities.extend(detect_ids(clean_text))
#         all_entities.extend(detect_cards(clean_text))
        
#     except Exception as e:
#         print(f"Warning: Detection encountered an error - {e}")
#         return []

#     final_clean_entities = resolve_overlaps(all_entities)
#     return final_clean_entities

# # --- TESTING BLOCK ---
# if __name__ == "__main__":
#     import json
#     print("--- Day 5 Real-World Input Tests ---\n")
    
#     # Test A: Messy spaces, tabs, and uppercase email
#     test_messy = "   Rahul \t\t Sharma has email RAHUL@GMAIL.COM   "
#     print("Test A: Messy Spaces and Uppercase Email")
#     print(f"Raw Input: '{test_messy}'")
    
#     # Let's show what the normalizer does before detecting
#     cleaned_input = normalize_text(test_messy)
#     print(f"Cleaned Input: '{cleaned_input}'")
#     print(json.dumps(detect_entities(test_messy), indent=2))
#     print("-" * 50)
    
#     # Test B: Boundary Check (Should NOT detect the phone number)
#     test_boundary = "My serial number is abc9876543210xyz."
#     print("Test B: Word Boundary Check")
#     print(f"Input: '{test_boundary}'")
#     results = detect_entities(test_boundary)
#     if not results:
#         print("Result: [] (Success! Boundary prevented false positive)")
#     else:
#         print(json.dumps(results, indent=2))


# Day 5 step 5 


# import spacy
# import re
# from config import MAX_TEXT_LENGTH  # <-- Import the new limit!

# nlp = None

# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ID": 3,
#     "CARD": 2,
#     "PERSON": 1
# }

# # --- 1. NORMALIZATION LAYER ---
# def normalize_text(text: str) -> str:
#     if text is None or not isinstance(text, str):
#         return ""
#     text = text.strip()
#     text = re.sub(r'\s+', ' ', text)
#     return text

# # --- 2. REGEX DETECTORS ---
# def detect_emails(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     for match in re.finditer(pattern, text, flags=re.IGNORECASE):
#         detected.append({"label": "EMAIL", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_phones(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "PHONE", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_ids(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "ID", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# def detect_cards(text: str) -> list:
#     if not text: return []
#     detected = []
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     for match in re.finditer(pattern, text):
#         detected.append({"label": "CARD", "text": match.group(), "start": match.start(), "end": match.end()})
#     return detected

# # --- 3. OVERLAP REFEREE ---
# def resolve_overlaps(spans: list) -> list:
#     if not spans: return []

#     sorted_spans = sorted(
#         spans, 
#         key=lambda x: (x['start'], -(x['end'] - x['start']), -PRIORITY_MAP.get(x['label'], 0))
#     )
    
#     clean_spans = []
#     for span in sorted_spans:
#         if not clean_spans:
#             clean_spans.append(span)
#         else:
#             last_span = clean_spans[-1]
#             if span['start'] < last_span['end']:
#                 last_length = last_span['end'] - last_span['start']
#                 current_length = span['end'] - span['start']
#                 if current_length > last_length:
#                     clean_spans[-1] = span
#             else:
#                 clean_spans.append(span)
                
#     return clean_spans

# # --- 4. MAIN ORCHESTRATOR ---
# def detect_entities(text: str) -> list:
#     # THE BOUNCER: Long Text Guard (Day 5, Step 5)
#     if text and len(text) > MAX_TEXT_LENGTH:
#         print(f"Warning: Text length ({len(text)}) exceeds the maximum allowed length ({MAX_TEXT_LENGTH}). Aborting.")
#         return []

#     # 1. Normalization Layer
#     clean_text = normalize_text(text)
    
#     if not clean_text:
#         return []
    
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model...")
#         nlp = spacy.load("en_core_web_sm")
    
#     all_entities = []
    
#     try:
#         doc = nlp(clean_text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 all_entities.append({
#                     "label": ent.label_, "text": ent.text,
#                     "start": ent.start_char, "end": ent.end_char
#                 })
                
#         all_entities.extend(detect_emails(clean_text))
#         all_entities.extend(detect_phones(clean_text))
#         all_entities.extend(detect_ids(clean_text))
#         all_entities.extend(detect_cards(clean_text))
        
#     except Exception as e:
#         print(f"Warning: Detection encountered an error - {e}")
#         return []

#     final_clean_entities = resolve_overlaps(all_entities)
#     return final_clean_entities

# # --- TESTING BLOCK ---
# if __name__ == "__main__":
#     print("--- Day 5 Step 5: Long Text Guard Test ---\n")
    
#     # Let's generate a massive string of text automatically!
#     # "A" * 15000 creates a string with 15,000 'A' characters
#     massive_text = "A" * 15000 
    
#     print(f"Attempting to process text of length: {len(massive_text)}...")
    
#     results = detect_entities(massive_text)
    
#     if not results:
#         print("Result: [] (Success! The bouncer blocked the massive text.)")
#     else:
#         print("Failed: The text slipped through the bouncer.")


# Day 5 final update :

# import spacy
# import re
# from config import MAX_TEXT_LENGTH

# # --- GLOBALS & CONFIG ---
# nlp = None

# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ID": 3,
#     "CARD": 2,
#     "PERSON": 1
# }

# # --- 1. NORMALIZATION LAYER ---
# def normalize_text(text: str) -> str:
#     """Cleans messy input text to ensure stable indices."""
#     if text is None or not isinstance(text, str):
#         return ""
#     text = text.strip()
#     text = re.sub(r'\s+', ' ', text)
#     return text

# # --- 2. AI DETECTOR (SpaCy) ---
# def detect_spacy_entities(text: str) -> list:
#     """Runs the AI model to extract PERSON entities."""
#     if not text: return []
    
#     global nlp
#     if nlp is None:
#         print("Loading spaCy model...")
#         nlp = spacy.load("en_core_web_sm")
        
#     detected = []
#     try:
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 detected.append({
#                     "label": ent.label_, "text": ent.text,
#                     "start": ent.start_char, "end": ent.end_char
#                 })
#     except Exception as e:
#         print(f"SpaCy Error: {e}")
        
#     return detected

# # --- 3. REGEX DETECTORS ---
# # Helper functions kept private with an underscore (_)
# def _detect_emails(text: str) -> list:
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     return [{"label": "EMAIL", "text": m.group(), "start": m.start(), "end": m.end()} for m in re.finditer(pattern, text, re.IGNORECASE)]

# def _detect_phones(text: str) -> list:
#     pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     return [{"label": "PHONE", "text": m.group(), "start": m.start(), "end": m.end()} for m in re.finditer(pattern, text)]

# def _detect_ids(text: str) -> list:
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()} for m in re.finditer(pattern, text)]

# def _detect_cards(text: str) -> list:
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()} for m in re.finditer(pattern, text)]

# def detect_regex_entities(text: str) -> list:
#     """Bundles all Regex rules into one clean function."""
#     if not text: return []
#     all_regex = []
#     all_regex.extend(_detect_emails(text))
#     all_regex.extend(_detect_phones(text))
#     all_regex.extend(_detect_ids(text))
#     all_regex.extend(_detect_cards(text))
#     return all_regex

# # --- 4. OVERLAP REFEREE ---
# def resolve_overlaps(spans: list) -> list:
#     """Resolves overlaps by length and priority map."""
#     if not spans: return []
#     sorted_spans = sorted(spans, key=lambda x: (x['start'], -(x['end'] - x['start']), -PRIORITY_MAP.get(x['label'], 0)))
#     clean_spans = []
#     for span in sorted_spans:
#         if not clean_spans:
#             clean_spans.append(span)
#         else:
#             last = clean_spans[-1]
#             if span['start'] < last['end']:
#                 if (span['end'] - span['start']) > (last['end'] - last['start']):
#                     clean_spans[-1] = span
#             else:
#                 clean_spans.append(span)
#     return clean_spans

# # --- 5. MAIN ORCHESTRATOR ---
# def detect_entities(raw_text: str) -> list:
#     """Master function: Normalizes, detects, and resolves all entities safely."""
#     # 1. Long Text Guard
#     if raw_text and len(raw_text) > MAX_TEXT_LENGTH:
#         print(f"Warning: Text exceeds max length ({MAX_TEXT_LENGTH}).")
#         return []

#     # 2. Normalize Text
#     clean_text = normalize_text(raw_text)
#     if not clean_text:
#         return []

#     # 3. Detect Entities
#     spacy_spans = detect_spacy_entities(clean_text)
#     regex_spans = detect_regex_entities(clean_text)
    
#     # 4. Merge and Resolve
#     combined_spans = spacy_spans + regex_spans
#     return resolve_overlaps(combined_spans)

# # --- TESTING BLOCK (Steps 6 & 7) ---
# if __name__ == "__main__":
#     import json
#     print("=== DAY 5 EDGE CASE GAUNTLET ===\n")
    
#     test_cases = [
#         {"name": "1. Empty String", "input": ""},
#         {"name": "2. None Input", "input": None},
#         {"name": "3. Numbers Only", "input": "1234567890"},
#         {"name": "4. Mixed Spacing (Index Stability)", "input": "  Rahul   Sharma   email   rahul@gmail.com  "},
#         {"name": "5. Massive Paragraph", "input": "This is a huge paragraph. " * 50 + "Call me at 9876543210."}
#     ]

#     for test in test_cases:
#         print(f"--- {test['name']} ---")
#         raw = test['input']
        
#         # Print raw vs cleaned to prove Step 6
#         if isinstance(raw, str) and len(raw) < 100:
#             print(f"RAW: '{raw}'")
#             print(f"CLEANED: '{normalize_text(raw)}'")
            
#         results = detect_entities(raw)
        
#         if not results:
#             print("Output: [] (Handled Safely)")
#         else:
#             print("Output:")
#             print(json.dumps(results, indent=2))
#         print("\n")



#final updated code temp 


"""
PII entity detection module.
Combines spaCy NER (PERSON) and regex patterns (EMAIL, PHONE, ID, CARD).
Returns spans relative to the original input text.
"""

# import re
# import logging
# from typing import List, Dict, Any

# import spacy
# from config import MAX_TEXT_LENGTH  # ensure this exists

# # Configure logger
# logger = logging.getLogger(__name__)

# # --- GLOBALS ---
# _nlp = None

# # Priority for overlap resolution (higher value = higher priority)
# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ID": 3,
#     "CARD": 2,
#     "PERSON": 1
# }


# def _get_spacy_model():
#     """Lazy-load spaCy model."""
#     global _nlp
#     if _nlp is None:
#         logger.info("Loading spaCy model 'en_core_web_sm'")
#         try:
#             _nlp = spacy.load("en_core_web_sm")
#         except OSError:
#             logger.error("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
#             raise
#     return _nlp


# # --- REGEX DETECTORS (private) ---
# def _detect_emails(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     return [{"label": "EMAIL", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_phones(text: str) -> List[Dict[str, Any]]:
#     # Simple pattern for demonstration; adjust as needed
#     pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     return [{"label": "PHONE", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_ids(text: str) -> List[Dict[str, Any]]:
#     # e.g., "1234 5678 9012"
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_cards(text: str) -> List[Dict[str, Any]]:
#     # e.g., "1234 5678 9012 3456"
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]


# def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
#     """Extract PERSON entities using spaCy NER."""
#     if not text:
#         return []
#     nlp = _get_spacy_model()
#     detected = []
#     try:
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 detected.append({
#                     "label": "PERSON",
#                     "text": ent.text,
#                     "start": ent.start_char,
#                     "end": ent.end_char
#                 })
#     except Exception as e:
#         logger.exception("SpaCy processing failed")
#     return detected


# def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
#     """Run all regex detectors and return combined list."""
#     if not text:
#         return []
#     entities = []
#     entities.extend(_detect_emails(text))
#     entities.extend(_detect_phones(text))
#     entities.extend(_detect_ids(text))
#     entities.extend(_detect_cards(text))
#     return entities


# def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """
#     Resolve overlapping spans using length and priority.
#     Keeps the longest span; if equal length, higher priority wins.
#     Assumes input spans are from the same text (no index shift).
#     """
#     if not entities:
#         return []

#     # Validate each entity
#     for idx, ent in enumerate(entities):
#         if not all(k in ent for k in ('label', 'start', 'end')):
#             raise ValueError(f"Entity {idx} missing required keys: {ent}")
#         if not isinstance(ent['start'], int) or not isinstance(ent['end'], int):
#             raise ValueError(f"Entity {idx} start/end must be integers: {ent}")
#         if ent['start'] < 0 or ent['end'] <= ent['start']:
#             raise ValueError(f"Entity {idx} has invalid span: {ent}")

#     # Sort: by start ascending, then by end descending (longer first), then by priority descending
#     sorted_ents = sorted(
#         entities,
#         key=lambda e: (e['start'], - (e['end'] - e['start']), -PRIORITY_MAP.get(e['label'], 0))
#     )

#     resolved = []
#     current = sorted_ents[0]

#     for next_ent in sorted_ents[1:]:
#         if next_ent['start'] < current['end']:  # overlap
#             # Keep the span with greater length; if equal, keep current (already highest priority due to sort)
#             if (next_ent['end'] - next_ent['start']) > (current['end'] - current['start']):
#                 current = next_ent
#         else:
#             resolved.append(current)
#             current = next_ent
#     resolved.append(current)

#     logger.debug("Resolved %d entities to %d", len(entities), len(resolved))
#     return resolved


# def detect_entities(raw_text: str) -> List[Dict[str, Any]]:
#     """
#     Main entry point: detect all PII entities in raw text.
#     Returns spans relative to the original input (no text modification).
#     """
#     # 1. Input validation and length guard
#     if raw_text is None:
#         return []
#     if not isinstance(raw_text, str):
#         raw_text = str(raw_text)

#     if len(raw_text) > MAX_TEXT_LENGTH:
#         logger.warning("Text exceeds max length (%d chars), returning empty", MAX_TEXT_LENGTH)
#         return []

#     # 2. Detect using both methods
#     spacy_spans = detect_spacy_entities(raw_text)
#     regex_spans = detect_regex_entities(raw_text)

#     # 3. Combine and resolve overlaps
#     combined = spacy_spans + regex_spans
#     if not combined:
#         return []

#     return resolve_overlaps(combined)




# final code for production


"""
PII entity detection module.
Combines spaCy NER (PERSON) and regex patterns (EMAIL, PHONE, ID, CARD).
Returns spans relative to the original input text (no modification).
"""

# import re
# import logging
# from typing import List, Dict, Any

# import spacy
# from .config import MAX_TEXT_LENGTH

# logger = logging.getLogger(__name__)

# # --- Globals ---
# _nlp = None

# # Priority for overlap resolution (higher value = higher priority)
# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ID": 3,
#     "CARD": 2,
#     "PERSON": 1
# }


# def _get_spacy_model():
#     """Lazy-load the spaCy model."""
#     global _nlp
#     if _nlp is None:
#         logger.info("Loading spaCy model 'en_core_web_sm'")
#         try:
#             _nlp = spacy.load("en_core_web_sm")
#         except OSError:
#             logger.error("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
#             raise
#     return _nlp

# def _get_spacy_model():
#     global _nlp
#     if _nlp is None:
#         logger.info("Loading spaCy model 'en_core_web_sm' (NER only)")
#         # Disable parser and tagger – we only need NER
#         _nlp = spacy.load("en_core_web_sm", disable=["parser", "tagger"])
#     return _nlp


# def _get_spacy_model():
#     """Lazy-load the spaCy model with only NER enabled (and its dependencies)."""
#     global _nlp
#     if _nlp is None:
#         logger.info("Loading spaCy model 'en_core_web_sm' (NER only)")
#         try:
#             # Disable all components except those required for NER (tok2vec, ner)
#             _nlp = spacy.load(
#                 "en_core_web_sm",
#                 disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]
#             )
#         except OSError:
#             logger.error("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
#             raise
    # return _nlp


# # --- Regex detectors (private) ---
# def _detect_emails(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     return [{"label": "EMAIL", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_phones(text: str) -> List[Dict[str, Any]]:
#     # Simplified pattern – adjust to your needs
#     pattern = r'\b(\+?\d{1,3}[\s-]?)?\d{5}[\s-]?\d{5}\b'
#     return [{"label": "PHONE", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_ids(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_cards(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]


# def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
#     """Extract PERSON entities using spaCy NER."""
#     if not text:
#         return []
#     nlp = _get_spacy_model()
#     detected = []
#     try:
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 detected.append({
#                     "label": "PERSON",
#                     "text": ent.text,
#                     "start": ent.start_char,
#                     "end": ent.end_char
#                 })
#     except Exception as e:
#         logger.exception("SpaCy processing failed")
#     return detected


# def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
#     """Run all regex detectors and return combined list."""
#     if not text:
#         return []
#     entities = []
#     entities.extend(_detect_emails(text))
#     entities.extend(_detect_phones(text))
#     entities.extend(_detect_ids(text))
#     entities.extend(_detect_cards(text))
#     return entities


# def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """
#     Resolve overlapping spans using length and priority.
#     Keeps the longest span; if equal length, higher priority wins.
#     Assumes input spans are from the same text (no index shift).
#     """
#     if not entities:
#         return []

#     # Validate each entity
#     for idx, ent in enumerate(entities):
#         if not all(k in ent for k in ('label', 'start', 'end')):
#             raise ValueError(f"Entity {idx} missing required keys: {ent}")
#         if not isinstance(ent['start'], int) or not isinstance(ent['end'], int):
#             raise ValueError(f"Entity {idx} start/end must be integers: {ent}")
#         if ent['start'] < 0 or ent['end'] <= ent['start']:
#             raise ValueError(f"Entity {idx} has invalid span: {ent}")

#     # Sort: by start ascending, then by end descending (longer first), then by priority descending
#     sorted_ents = sorted(
#         entities,
#         key=lambda e: (e['start'], - (e['end'] - e['start']), -PRIORITY_MAP.get(e['label'], 0))
#     )

#     resolved = []
#     current = sorted_ents[0]

#     for next_ent in sorted_ents[1:]:
#         if next_ent['start'] < current['end']:  # overlap
#             # Keep the span with greater length; if equal, keep current (already higher priority)
#             if (next_ent['end'] - next_ent['start']) > (current['end'] - current['start']):
#                 current = next_ent
#         else:
#             resolved.append(current)
#             current = next_ent
#     resolved.append(current)

#     logger.debug("Resolved %d entities to %d", len(entities), len(resolved))
#     return resolved


# def detect_entities(raw_text: str) -> List[Dict[str, Any]]:
#     """
#     Main entry point: detect all PII entities in raw text.
#     Returns spans relative to the original input (no text modification).
#     """
#     # 1. Input validation and length guard
#     if raw_text is None:
#         return []
#     if not isinstance(raw_text, str):
#         raw_text = str(raw_text)

#     if len(raw_text) > MAX_TEXT_LENGTH:
#         logger.warning("Text exceeds max length (%d chars), returning empty", MAX_TEXT_LENGTH)
#         return []

#     # 2. Detect using both methods
#     spacy_spans = detect_spacy_entities(raw_text)
#     regex_spans = detect_regex_entities(raw_text)

#     # 3. Combine and resolve overlaps
#     combined = spacy_spans + regex_spans
#     if not combined:
#         return []

#     return resolve_overlaps(combined)


# NEW code update 

"""
PII entity detection module.
Combines spaCy NER (PERSON) and regex patterns (EMAIL, PHONE, ID, CARD, ADDRESS).
Includes a fallback heuristic for names (capitalized word sequences) when spaCy returns none.
Spans are relative to the original input text (no modification).
"""

# import re
# import logging
# from typing import List, Dict, Any, Optional

# import spacy
# from .config import MAX_TEXT_LENGTH

# logger = logging.getLogger(__name__)

# # --- Globals ---
# _nlp: Optional[spacy.Language] = None

# # Priority for overlap resolution (higher value = higher priority)
# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ADDRESS": 3,
#     "ID": 2,
#     "CARD": 2,
#     "PERSON": 1
# }


# def _get_spacy_model() -> spacy.Language:
#     """Lazy‑load the spaCy model with only NER enabled (and its dependencies)."""
#     global _nlp
#     if _nlp is None:
#         logger.info("Loading spaCy model 'en_core_web_sm' (NER only)")
#         try:
#             # Disable components not needed for NER
#             _nlp = spacy.load(
#                 "en_core_web_sm",
#                 disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]
#             )
#         except OSError:
#             logger.error("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
#             raise
#     return _nlp


# # ----------------------------------------------------------------------
# # Regex detectors (private)
# # ----------------------------------------------------------------------

# def _detect_emails(text: str) -> List[Dict[str, Any]]:
#     """Extract email addresses."""
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     return [
#         {"label": "EMAIL", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]


# def _detect_phones(text: str) -> List[Dict[str, Any]]:
#     """
#     Extract phone numbers in various formats.
#     Simplified robust pattern with fallback.
#     """
#     # Primary pattern – handles most common formats
#     primary_pattern = r'''
#         (?:\+?\d{1,3}[-.\s]?)?          # optional country code
#         \(?\d{3}\)?[-.\s]?              # area code (optional parentheses)
#         \d{3}[-.\s]?                    # prefix
#         \d{4}                            # line number
#         (?:\s*(?:#|x\.?|ext\.?)\s*\d+)?  # optional extension
#     '''
#     try:
#         compiled = re.compile(primary_pattern, re.VERBOSE)
#     except re.error as e:
#         logger.error(f"Phone regex compilation failed: {e}, using fallback pattern")
#         # Fallback: just 10 consecutive digits
#         compiled = re.compile(r'\b\d{10}\b')
#     return [
#         {"label": "PHONE", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in compiled.finditer(text)
#     ]


# def _detect_ids(text: str) -> List[Dict[str, Any]]:
#     """
#     Extract ID‑like numbers (e.g., 1234 5678 9012, 1234-5678-9012).
#     """
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [
#         {"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]


# def _detect_cards(text: str) -> List[Dict[str, Any]]:
#     """
#     Extract credit/debit card numbers (16 digits, optionally grouped).
#     """
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [
#         {"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]


# def _detect_addresses(text: str) -> List[Dict[str, Any]]:
#     """
#     Detect US‑style addresses: number + street name, optionally followed by city, state, ZIP.
#     Examples: 123 Main St, 123 Main St, Springfield, IL 62701
#     """
#     pattern = r'''
#         \b\d{1,5}                         # street number (1-5 digits)
#         \s+                                # space
#         [A-Za-z0-9\s\.\-]+                  # street name (allow letters, numbers, spaces, dots, hyphens)
#         (?:                                 # optional city/state/zip block
#             (?:,\s+|\s+)                     # separator
#             [A-Z][a-zA-Z\s]+                  # city (capitalized words)
#             (?:,\s+|\s+)                       # separator
#             [A-Z]{2}                           # state (2 uppercase letters)
#             \s+                                 # space
#             \d{5}(?:-\d{4})?                    # ZIP (5 or 9 digits)
#         )?
#     '''
#     try:
#         compiled = re.compile(pattern, re.VERBOSE | re.IGNORECASE)
#     except re.error as e:
#         logger.error(f"Address regex compilation failed: {e}")
#         return []

#     matches = []
#     for m in compiled.finditer(text):
#         # Filter out very short matches (e.g., "1 Main St" is ok; we set a minimum length)
#         if len(m.group()) > 10:
#             matches.append({
#                 "label": "ADDRESS",
#                 "text": m.group(),
#                 "start": m.start(),
#                 "end": m.end()
#             })
#     return matches


# def _detect_names_fallback(text: str) -> List[Dict[str, Any]]:
#     """
#     Fallback heuristic: detect sequences of capitalized words as potential PERSON names.
#     Used only when spaCy finds zero PERSON entities.
#     """
#     pattern = r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
#     return [
#         {"label": "PERSON", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]


# # ----------------------------------------------------------------------
# # Public detection functions
# # ----------------------------------------------------------------------

# def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
#     """Extract PERSON entities using spaCy NER."""
#     if not text:
#         return []
#     nlp = _get_spacy_model()
#     detected = []
#     try:
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 detected.append({
#                     "label": "PERSON",
#                     "text": ent.text,
#                     "start": ent.start_char,
#                     "end": ent.end_char
#                 })
#     except Exception as e:
#         logger.exception("SpaCy processing failed")
#     return detected


# def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
#     """Run all regex detectors and return combined list."""
#     if not text:
#         return []
#     entities = []
#     try:
#         entities.extend(_detect_emails(text))
#         entities.extend(_detect_phones(text))
#         entities.extend(_detect_ids(text))
#         entities.extend(_detect_cards(text))
#         entities.extend(_detect_addresses(text))
#     except Exception as e:
#         logger.exception("Regex detection failed")
#     return entities


# def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """
#     Resolve overlapping spans using length and priority.
#     Keeps the longest span; if equal length, higher priority wins.
#     Assumes input spans are from the same text (no index shift).
#     """
#     if not entities:
#         return []

#     # Validate each entity
#     for idx, ent in enumerate(entities):
#         if not all(k in ent for k in ('label', 'start', 'end')):
#             raise ValueError(f"Entity {idx} missing required keys: {ent}")
#         if not isinstance(ent['start'], int) or not isinstance(ent['end'], int):
#             raise ValueError(f"Entity {idx} start/end must be integers: {ent}")
#         if ent['start'] < 0 or ent['end'] <= ent['start']:
#             raise ValueError(f"Entity {idx} has invalid span: {ent}")

#     # Sort: by start ascending, then by end descending (longer first), then by priority descending
#     sorted_ents = sorted(
#         entities,
#         key=lambda e: (e['start'], - (e['end'] - e['start']), -PRIORITY_MAP.get(e['label'], 0))
#     )

#     resolved = []
#     current = sorted_ents[0]

#     for next_ent in sorted_ents[1:]:
#         if next_ent['start'] < current['end']:  # overlap
#             # Keep the span with greater length; if equal, keep current (already higher priority)
#             if (next_ent['end'] - next_ent['start']) > (current['end'] - current['start']):
#                 current = next_ent
#         else:
#             resolved.append(current)
#             current = next_ent
#     resolved.append(current)

#     logger.debug("Resolved %d entities to %d", len(entities), len(resolved))
#     return resolved


# def detect_entities(raw_text: str) -> List[Dict[str, Any]]:
#     """
#     Main entry point: detect all PII entities in raw text.
#     Returns spans relative to the original input (no text modification).

#     Steps:
#         1. Input validation and length guard.
#         2. Detect using spaCy (PERSON).
#         3. Detect using regex (EMAIL, PHONE, ID, CARD, ADDRESS).
#         4. If no PERSON found by spaCy, apply fallback name heuristic.
#         5. Combine all spans and resolve overlaps.
#     """
#     # 1. Input validation and length guard
#     if raw_text is None:
#         return []
#     if not isinstance(raw_text, str):
#         raw_text = str(raw_text)

#     if len(raw_text) > MAX_TEXT_LENGTH:
#         logger.warning("Text exceeds max length (%d chars), returning empty", MAX_TEXT_LENGTH)
#         return []

#     # 2. Detect using both methods
#     spacy_spans = detect_spacy_entities(raw_text)
#     regex_spans = detect_regex_entities(raw_text)

#     # 3. Fallback: if no PERSON from spaCy, try heuristic name detection
#     fallback_spans = []
#     if not any(span['label'] == 'PERSON' for span in spacy_spans):
#         fallback_spans = _detect_names_fallback(raw_text)
#         if fallback_spans:
#             logger.info("Fallback name detection found %d potential names", len(fallback_spans))

#     # 4. Combine and resolve overlaps
#     combined = spacy_spans + regex_spans + fallback_spans
#     if not combined:
#         return []

#     return resolve_overlaps(combined)



# # DAY 16 final update 
# """
# PII entity detection module.
# Combines spaCy NER (PERSON) and regex patterns (EMAIL, PHONE, ID, CARD, ADDRESS, ORG).
# Includes fallback for capitalized names (including single words) and all‑caps words as ORG.
# Spans are relative to the original input text (no modification).
# """

# import re
# import logging
# from typing import List, Dict, Any, Optional

# import spacy
# from .config import MAX_TEXT_LENGTH

# logger = logging.getLogger(__name__)

# # --- Globals ---
# _nlp: Optional[spacy.Language] = None

# # Priority for overlap resolution (higher value = higher priority)
# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ADDRESS": 3,
#     "ID": 2,
#     "CARD": 2,
#     "ORG": 1,
#     "PERSON": 1
# }


# def _get_spacy_model() -> spacy.Language:
#     """Lazy‑load the spaCy model with only NER enabled."""
#     global _nlp
#     if _nlp is None:
#         logger.info("Loading spaCy model 'en_core_web_sm' (NER only)")
#         try:
#             _nlp = spacy.load(
#                 "en_core_web_sm",
#                 disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]
#             )
#         except OSError:
#             logger.error("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
#             raise
#     return _nlp


# # ----------------------------------------------------------------------
# # Regex detectors (private)
# # ----------------------------------------------------------------------

# def _detect_emails(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     return [
#         {"label": "EMAIL", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]


# def _detect_phones(text: str) -> List[Dict[str, Any]]:
#     pattern = r'''
#         (?:\+?\d{1,3}[-.\s]?)?          # optional country code
#         \(?\d{3}\)?[-.\s]?              # area code (optional parentheses)
#         \d{3}[-.\s]?                    # prefix
#         \d{4}                            # line number
#         (?:\s*(?:#|x\.?|ext\.?)\s*\d+)?  # optional extension
#     '''
#     try:
#         compiled = re.compile(pattern, re.VERBOSE)
#     except re.error as e:
#         logger.error(f"Phone regex compilation failed: {e}, using fallback pattern")
#         compiled = re.compile(r'\b\d{10}\b')
#     return [
#         {"label": "PHONE", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in compiled.finditer(text)
#     ]


# def _detect_ids(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [
#         {"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]


# def _detect_cards(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [
#         {"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]


# def _detect_addresses(text: str) -> List[Dict[str, Any]]:
#     pattern = r'''
#         \b\d{1,5}                         # street number (1-5 digits)
#         \s+                                # space
#         [A-Za-z0-9\s\.\-]+                  # street name (allow letters, numbers, spaces, dots, hyphens)
#         (?:                                 # optional city/state/zip block
#             (?:,\s+|\s+)                     # separator
#             [A-Z][a-zA-Z\s]+                  # city (capitalized words)
#             (?:,\s+|\s+)                       # separator
#             [A-Z]{2}                           # state (2 uppercase letters)
#             \s+                                 # space
#             \d{5}(?:-\d{4})?                    # ZIP (5 or 9 digits)
#         )?
#     '''
#     try:
#         compiled = re.compile(pattern, re.VERBOSE | re.IGNORECASE)
#     except re.error as e:
#         logger.error(f"Address regex compilation failed: {e}")
#         return []
#     matches = []
#     for m in compiled.finditer(text):
#         if len(m.group()) > 10:
#             matches.append({
#                 "label": "ADDRESS",
#                 "text": m.group(),
#                 "start": m.start(),
#                 "end": m.end()
#             })
#     return matches


# def _detect_organizations(text: str) -> List[Dict[str, Any]]:
#     """Detect all‑caps words (≥2 letters) as potential organizations."""
#     pattern = r'\b[A-Z]{2,}\b'
#     return [
#         {"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]


# def _detect_names_fallback(text: str) -> List[Dict[str, Any]]:
#     """
#     Fallback name detection:
#     - Multi‑word capitalized sequences (e.g., "Rahul Sharma")
#     - Single capitalized words (≥2 letters) that are not at sentence start? We'll include all.
#     """
#     multi_word = r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
#     single_word = r'\b[A-Z][a-z]{1,}\b'   # single capitalized word (at least 2 letters)
#     combined_pattern = f'({multi_word})|({single_word})'
#     matches = re.finditer(combined_pattern, text)
#     return [
#         {"label": "PERSON", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in matches
#     ]


# # ----------------------------------------------------------------------
# # Public detection functions
# # ----------------------------------------------------------------------

# # def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
# #     if not text:
# #         return []
# #     nlp = _get_spacy_model()
# #     detected = []
# #     try:
# #         doc = nlp(text)
# #         for ent in doc.ents:
# #             if ent.label_ == "PERSON":
# #                 detected.append({
# #                     "label": "PERSON",
# #                     "text": ent.text,
# #                     "start": ent.start_char,
# #                     "end": ent.end_char
# #                 })
# #     except Exception as e:
# #         logger.exception("SpaCy processing failed")
# #     return detected
# def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
#     """Extract PERSON and ORG entities using spaCy NER."""
#     if not text:
#         return []
#     nlp = _get_spacy_model()
#     detected = []
#     try:
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 detected.append({
#                     "label": "PERSON",
#                     "text": ent.text,
#                     "start": ent.start_char,
#                     "end": ent.end_char
#                 })
#             elif ent.label_ == "ORG":
#                 detected.append({
#                     "label": "ORG",
#                     "text": ent.text,
#                     "start": ent.start_char,
#                     "end": ent.end_char
#                 })
#     except Exception as e:
#         logger.exception("SpaCy processing failed")
#     return detected


# def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
#     if not text:
#         return []
#     entities = []
#     try:
#         entities.extend(_detect_emails(text))
#         entities.extend(_detect_phones(text))
#         entities.extend(_detect_ids(text))
#         entities.extend(_detect_cards(text))
#         entities.extend(_detect_addresses(text))
#         entities.extend(_detect_organizations(text))
#     except Exception as e:
#         logger.exception("Regex detection failed")
#     return entities


# def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     if not entities:
#         return []

#     for idx, ent in enumerate(entities):
#         if not all(k in ent for k in ('label', 'start', 'end')):
#             raise ValueError(f"Entity {idx} missing required keys: {ent}")
#         if not isinstance(ent['start'], int) or not isinstance(ent['end'], int):
#             raise ValueError(f"Entity {idx} start/end must be integers: {ent}")
#         if ent['start'] < 0 or ent['end'] <= ent['start']:
#             raise ValueError(f"Entity {idx} has invalid span: {ent}")

#     sorted_ents = sorted(
#         entities,
#         key=lambda e: (e['start'], - (e['end'] - e['start']), -PRIORITY_MAP.get(e['label'], 0))
#     )

#     resolved = []
#     current = sorted_ents[0]

#     for next_ent in sorted_ents[1:]:
#         if next_ent['start'] < current['end']:
#             if (next_ent['end'] - next_ent['start']) > (current['end'] - current['start']):
#                 current = next_ent
#         else:
#             resolved.append(current)
#             current = next_ent
#     resolved.append(current)

#     logger.debug("Resolved %d entities to %d", len(entities), len(resolved))
#     return resolved


# def detect_entities(raw_text: str) -> List[Dict[str, Any]]:
#     if raw_text is None:
#         return []
#     if not isinstance(raw_text, str):
#         raw_text = str(raw_text)

#     if len(raw_text) > MAX_TEXT_LENGTH:
#         logger.warning("Text exceeds max length (%d chars), returning empty", MAX_TEXT_LENGTH)
#         return []

#     spacy_spans = detect_spacy_entities(raw_text)
#     regex_spans = detect_regex_entities(raw_text)

#     # Fallback: if no PERSON from spaCy, use heuristic name detection
#     fallback_spans = []
#     if not any(span['label'] == 'PERSON' for span in spacy_spans):
#         fallback_spans = _detect_names_fallback(raw_text)
#         if fallback_spans:
#             logger.info("Fallback name detection found %d potential names", len(fallback_spans))

#     combined = spacy_spans + regex_spans + fallback_spans
#     if not combined:
#         return []

#     return resolve_overlaps(combined)


# final update in day 16 
"""
PII entity detection module.
Combines spaCy NER (PERSON, ORG) and regex patterns (EMAIL, PHONE, ID, CARD, ADDRESS, ORG).
Includes fallback for capitalized names (including single words) and a common‑name list for ORG.
Spans are relative to the original input text (no modification).
"""

# import re
# import logging
# from typing import List, Dict, Any, Optional

# import spacy
# from .config import MAX_TEXT_LENGTH

# logger = logging.getLogger(__name__)

# # --- Globals ---
# _nlp: Optional[spacy.Language] = None

# # Priority for overlap resolution
# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ADDRESS": 3,
#     "ID": 2,
#     "CARD": 2,
#     "ORG": 1,
#     "PERSON": 1
# }

# def _get_spacy_model() -> spacy.Language:
#     """Lazy‑load the spaCy model with only NER enabled."""
#     global _nlp
#     if _nlp is None:
#         logger.info("Loading spaCy model 'en_core_web_sm' (NER only)")
#         try:
#             _nlp = spacy.load(
#                 "en_core_web_sm",
#                 disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]
#             )
#         except OSError:
#             logger.error("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
#             raise
#     return _nlp


# # ----------------------------------------------------------------------
# # Regex detectors (private)
# # ----------------------------------------------------------------------

# def _detect_emails(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     return [
#         {"label": "EMAIL", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]

# def _detect_phones(text: str) -> List[Dict[str, Any]]:
#     pattern = r'''
#         (?:\+?\d{1,3}[-.\s]?)?          # optional country code
#         \(?\d{3}\)?[-.\s]?              # area code (optional parentheses)
#         \d{3}[-.\s]?                    # prefix
#         \d{4}                            # line number
#         (?:\s*(?:#|x\.?|ext\.?)\s*\d+)?  # optional extension
#     '''
#     try:
#         compiled = re.compile(pattern, re.VERBOSE)
#     except re.error as e:
#         logger.error(f"Phone regex compilation failed: {e}, using fallback pattern")
#         compiled = re.compile(r'\b\d{10}\b')
#     return [
#         {"label": "PHONE", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in compiled.finditer(text)
#     ]

# def _detect_ids(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [
#         {"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]

# def _detect_cards(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [
#         {"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]

# def _detect_addresses(text: str) -> List[Dict[str, Any]]:
#     pattern = r'''
#         \b\d{1,5}                         # street number (1-5 digits)
#         \s+                                # space
#         [A-Za-z0-9\s\.\-]+                  # street name
#         (?:                                 # optional city/state/zip block
#             (?:,\s+|\s+)                     # separator
#             [A-Z][a-zA-Z\s]+                  # city
#             (?:,\s+|\s+)                       # separator
#             [A-Z]{2}                           # state
#             \s+                                 # space
#             \d{5}(?:-\d{4})?                    # ZIP
#         )?
#     '''
#     try:
#         compiled = re.compile(pattern, re.VERBOSE | re.IGNORECASE)
#     except re.error as e:
#         logger.error(f"Address regex compilation failed: {e}")
#         return []
#     matches = []
#     for m in compiled.finditer(text):
#         if len(m.group()) > 10:
#             matches.append({
#                 "label": "ADDRESS",
#                 "text": m.group(),
#                 "start": m.start(),
#                 "end": m.end()
#             })
#     return matches

# def _detect_allcaps_orgs(text: str) -> List[Dict[str, Any]]:
#     """Detect all‑caps words (≥2 letters) as potential organizations."""
#     pattern = r'\b[A-Z]{2,}\b'
#     return [
#         {"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in re.finditer(pattern, text)
#     ]

# def _detect_common_orgs(text: str) -> List[Dict[str, Any]]:
#     """
#     Detect common organization names (case‑insensitive) from a predefined list.
#     This catches lowercase, capitalized, and uppercase variants.
#     """
#     # Common company names (add more as needed)
#     common_orgs = {
#         "google", "microsoft", "apple", "amazon", "facebook", "meta",
#         "ibm", "intel", "oracle", "sap", "salesforce", "adobe",
#         "netflix", "spotify", "twitter", "x", "linkedin", "whatsapp",
#         "youtube", "instagram", "tiktok", "snapchat", "reddit", "discord",
#         "slack", "zoom", "teams", "outlook", "gmail", "yahoo", "bing"
#     }
#     # Escape names to avoid regex special characters, then join with |
#     pattern = r'\b(' + '|'.join(re.escape(name) for name in common_orgs) + r')\b'
#     compiled = re.compile(pattern, re.IGNORECASE)
#     return [
#         {"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in compiled.finditer(text)
#     ]

# def _detect_names_fallback(text: str) -> List[Dict[str, Any]]:
#     """
#     Fallback name detection:
#     - Multi‑word capitalized sequences (e.g., "Rahul Sharma")
#     - Single capitalized words (≥2 letters)
#     """
#     multi_word = r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
#     single_word = r'\b[A-Z][a-z]{1,}\b'
#     combined_pattern = f'({multi_word})|({single_word})'
#     matches = re.finditer(combined_pattern, text)
#     return [
#         {"label": "PERSON", "text": m.group(), "start": m.start(), "end": m.end()}
#         for m in matches
#     ]


# # ----------------------------------------------------------------------
# # Public detection functions
# # ----------------------------------------------------------------------

# def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
#     """Extract PERSON and ORG entities using spaCy NER."""
#     if not text:
#         return []
#     nlp = _get_spacy_model()
#     detected = []
#     try:
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ == "PERSON":
#                 detected.append({
#                     "label": "PERSON",
#                     "text": ent.text,
#                     "start": ent.start_char,
#                     "end": ent.end_char
#                 })
#             elif ent.label_ == "ORG":
#                 detected.append({
#                     "label": "ORG",
#                     "text": ent.text,
#                     "start": ent.start_char,
#                     "end": ent.end_char
#                 })
#     except Exception as e:
#         logger.exception("SpaCy processing failed")
#     return detected

# def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
#     if not text:
#         return []
#     entities = []
#     try:
#         entities.extend(_detect_emails(text))
#         entities.extend(_detect_phones(text))
#         entities.extend(_detect_ids(text))
#         entities.extend(_detect_cards(text))
#         entities.extend(_detect_addresses(text))
#         entities.extend(_detect_allcaps_orgs(text))      # for "GOOGLE"
#         entities.extend(_detect_common_orgs(text))       # for "google", "Google"
#     except Exception as e:
#         logger.exception("Regex detection failed")
#     return entities

# def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     # ... (unchanged, same as before) ...
#     if not entities:
#         return []

#     for idx, ent in enumerate(entities):
#         if not all(k in ent for k in ('label', 'start', 'end')):
#             raise ValueError(f"Entity {idx} missing required keys: {ent}")
#         if not isinstance(ent['start'], int) or not isinstance(ent['end'], int):
#             raise ValueError(f"Entity {idx} start/end must be integers: {ent}")
#         if ent['start'] < 0 or ent['end'] <= ent['start']:
#             raise ValueError(f"Entity {idx} has invalid span: {ent}")

#     sorted_ents = sorted(
#         entities,
#         key=lambda e: (e['start'], - (e['end'] - e['start']), -PRIORITY_MAP.get(e['label'], 0))
#     )

#     resolved = []
#     current = sorted_ents[0]

#     for next_ent in sorted_ents[1:]:
#         if next_ent['start'] < current['end']:
#             if (next_ent['end'] - next_ent['start']) > (current['end'] - current['start']):
#                 current = next_ent
#         else:
#             resolved.append(current)
#             current = next_ent
#     resolved.append(current)

#     logger.debug("Resolved %d entities to %d", len(entities), len(resolved))
#     return resolved

# def detect_entities(raw_text: str) -> List[Dict[str, Any]]:
#     # ... (unchanged) ...
#     if raw_text is None:
#         return []
#     if not isinstance(raw_text, str):
#         raw_text = str(raw_text)

#     if len(raw_text) > MAX_TEXT_LENGTH:
#         logger.warning("Text exceeds max length (%d chars), returning empty", MAX_TEXT_LENGTH)
#         return []

#     spacy_spans = detect_spacy_entities(raw_text)
#     regex_spans = detect_regex_entities(raw_text)

#     # Fallback name detection if no PERSON from spaCy
#     fallback_spans = []
#     if not any(span['label'] == 'PERSON' for span in spacy_spans):
#         fallback_spans = _detect_names_fallback(raw_text)
#         if fallback_spans:
#             logger.info("Fallback name detection found %d potential names", len(fallback_spans))

#     combined = spacy_spans + regex_spans + fallback_spans
#     if not combined:
#         return []

#     return resolve_overlaps(combined)



# Day 17 final code update

# """
# PII entity detection module.
# Combines spaCy NER and extensive regex for global PII detection:
# - Names (PERSON) via spaCy + case‑insensitive common name list + capitalized fallback
# - Organizations (ORG) via spaCy + common org list + all‑caps fallback
# - Emails, Phones, Credit Cards, Aadhaar (India ID), generic IDs, Addresses
# All regex patterns are robust and case‑insensitive where appropriate.
# """

# import re
# import logging
# from typing import List, Dict, Any, Optional

# import spacy
# from .config import MAX_TEXT_LENGTH

# logger = logging.getLogger(__name__)

# # ----------------------------------------------------------------------
# # Globals
# # ----------------------------------------------------------------------
# _nlp: Optional[spacy.Language] = None

# # Priority for overlap resolution (higher = more important)
# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ADDRESS": 3,
#     "AADHAAR": 2,
#     "CARD": 2,
#     "ID": 2,
#     "ORG": 1,
#     "PERSON": 1
# }

# # ----------------------------------------------------------------------
# # spaCy model (lazy‑loaded, NER only)
# # ----------------------------------------------------------------------
# def _get_spacy_model() -> spacy.Language:
#     global _nlp
#     if _nlp is None:
#         logger.info("Loading spaCy model 'en_core_web_sm' (NER only)")
#         try:
#             _nlp = spacy.load(
#                 "en_core_web_sm",
#                 disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]
#             )
#         except OSError:
#             logger.error("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
#             raise
#     return _nlp

# # ----------------------------------------------------------------------
# # Common name list (case‑insensitive) – covers Indian & foreign names
# # ----------------------------------------------------------------------
# COMMON_NAMES = {
#     # Indian names (male/female)
#     "ram", "rama", "shyam", "ravi", "kumar", "priya", "anita", "raj", "rani",
#     "amit", "sunil", "vijay", "ajay", "suresh", "mahesh", "nisha", "pooja",
#     "deepak", "neha", "vikas", "rakesh", "sita", "gita", "lakshmi", "krishna",
#     "arjun", "bharat", "karan", "arav", "vihaan", "advik", "anaya", "diya",
#     "atharv", "vivaan", "pranav", "sai", "ishaan", "dhruv", "kavya", "aditi",
#     "tanvi", "aarav", "vihaan", "vivaan", "ananya", "anika", "aryan", "ishan",
#     "rohan", "mohit", "sahil", "naveen", "pawan", "manoj", "jatin", "tarun",
#     "abhishek", "ankit", "gaurav", "hitesh", "kunal", "lalit", "mayank",
#     "nilesh", "parth", "rajat", "sachin", "tushar", "umesh", "vikram",
#     "yogesh", "bhavna", "chandni", "divya", "ekta", "falguni", "geeta",
#     "hemal", "ishita", "jaya", "kajal", "kiran", "lata", "madhu", "nandini",
#     "payal", "rekha", "shanti", "tina", "urvi", "vandana", "yashoda",
#     # Western names
#     "john", "jane", "mike", "sarah", "david", "lisa", "paul", "anna",
#     "james", "mary", "robert", "patricia", "william", "jennifer", "richard",
#     "linda", "joseph", "barbara", "thomas", "susan", "charles", "margaret",
#     "christopher", "jessica", "daniel", "emily", "matthew", "ashley",
#     "anthony", "kimberly", "donald", "sandra", "mark", "melissa", "steven",
#     "elizabeth", "andrew", "amy", "kenneth", "carol", "joshua", "michelle",
#     "kevin", "rebecca", "brian", "laura", "george", "karen", "edward",
#     "deborah", "ronald", "cynthia", "timothy", "angela", "jason", "sharon",
#     "jeffrey", "pamela", "ryan", "kathleen", "jacob", "helen", "gary",
#     "shirley", "nicholas", "emma", "eric", "carolyn", "stephen", "janet",
#     "larry", "catherine", "justin", "christine", "scott", "heather",
#     "brandon", "diane", "benjamin", "julie", "samuel", "joyce", "gregory",
#     "victoria", "alexander", "kelly", "patrick", "christina", "frank",
#     "lauren", "raymond", "frances", "jack", "martha", "henry", "judith",
#     "jerry", "cheryl", "aaron", "megan", "louis", "andrea", "charles",
#     "tiffany", "russell", "amber", "bobby", "danielle", "phillip", "abigail",
#     # Additional global names
#     "mohammed", "ali", "fatima", "ahmed", "omar", "layla", "hassan", "hussain",
#     "wei", "li", "chen", "wang", "zhang", "liu", "yang", "huang", "feng",
#     "jose", "maria", "carlos", "ana", "luis", "juan", "diego", "sofia",
#     "sergei", "olga", "dmitry", "natalia", "ivan", "tatyana", "vladimir",
#     "hiroshi", "yuki", "takashi", "sakura", "kenji", "akira", "yuto",
#     "emiko", "haruto", "hinata", "himari", "ren", "souta", "mei", "yuna",
#     "kim", "lee", "park", "choi", "jung", "kang", "yoon", "lim", "han",
#     "soo", "min", "ji", "hyun", "seo", "jin", "woo", "young"
# }

# # Common organization names (case‑insensitive)
# COMMON_ORGS = {
#     "google", "microsoft", "apple", "amazon", "facebook", "meta", "netflix",
#     "spotify", "twitter", "x", "linkedin", "whatsapp", "youtube", "instagram",
#     "tiktok", "snapchat", "reddit", "discord", "slack", "zoom", "teams",
#     "outlook", "gmail", "yahoo", "bing", "baidu", "yandex", "oracle", "ibm",
#     "intel", "amd", "nvidia", "samsung", "sony", "panasonic", "lg", "philips",
#     "huawei", "xiaomi", "oppo", "vivo", "oneplus", "nokia", "motorola",
#     "porsche", "ferrari", "lamborghini", "bmw", "mercedes", "audi", "toyota",
#     "honda", "ford", "chevrolet", "volkswagen", "hyundai", "kia", "tesla",
#     "adidas", "nike", "puma", "reebok", "zara", "h&m", "gucci", "prada",
#     "chanel", "louis vuitton", "hermes", "cartier", "rolex", "omega",
#     "coca-cola", "pepsi", "starbucks", "mcdonald's", "kfc", "burger king",
#     "subway", "domino's", "pizza hut", "walmart", "target", "costco",
#     "ikea", "home depot", "lowe's", "ebay", "paypal", "visa", "mastercard",
#     "american express", "discover", "jpmorgan", "goldman sachs", "morgan stanley"
# }

# # ----------------------------------------------------------------------
# # Regex detectors (private) – each returns list of entity dicts
# # ----------------------------------------------------------------------
# def _detect_emails(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     return [{"label": "EMAIL", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_phones(text: str) -> List[Dict[str, Any]]:
#     # International phone numbers (simplified but covers most)
#     patterns = [
#         r'\+\d{1,3}[-.\s]?\d{4,14}',               # +1 234 567 8900
#         r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',    # (123) 456-7890, 123-456-7890
#         r'\b\d{5}[-.\s]?\d{5}\b',                   # Indian mobile: 98765 43210
#     ]
#     combined = '|'.join(f'(?:{p})' for p in patterns)
#     compiled = re.compile(combined, re.VERBOSE)
#     return [{"label": "PHONE", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in compiled.finditer(text)]

# def _detect_cards(text: str) -> List[Dict[str, Any]]:
#     # Credit/debit card numbers (16 digits, optional spaces/hyphens)
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_aadhaar(text: str) -> List[Dict[str, Any]]:
#     # Aadhaar: 12 digits, optional spaces/hyphens after every 4 digits
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "AADHAAR", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_ids(text: str) -> List[Dict[str, Any]]:
#     # Generic IDs: sequences of 9+ digits (excluding those caught by AADHAAR/CARD)
#     pattern = r'\b\d{9,}\b'
#     return [{"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_addresses(text: str) -> List[Dict[str, Any]]:
#     # Simplified address: street number + street name (at least 3 words)
#     pattern = r'\b\d{1,5}\s+[A-Za-z]+(?:\s+[A-Za-z]+){1,4}(?:\s+(?:road|rd|street|st|avenue|ave|lane|ln|drive|dr|court|ct|plaza|way))?\b'
#     compiled = re.compile(pattern, re.IGNORECASE)
#     matches = []
#     for m in compiled.finditer(text):
#         if len(m.group()) > 10:
#             matches.append({"label": "ADDRESS", "text": m.group(), "start": m.start(), "end": m.end()})
#     return matches

# def _detect_common_names(text: str) -> List[Dict[str, Any]]:
#     """Case‑insensitive matching of common personal names."""
#     pattern = r'\b(' + '|'.join(re.escape(name) for name in COMMON_NAMES) + r')\b'
#     compiled = re.compile(pattern, re.IGNORECASE)
#     return [{"label": "PERSON", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in compiled.finditer(text)]

# def _detect_common_orgs(text: str) -> List[Dict[str, Any]]:
#     """Case‑insensitive matching of common organization names."""
#     # Escape names and join (names may contain apostrophes, dots, etc.)
#     escaped = [re.escape(name) for name in COMMON_ORGS]
#     pattern = r'\b(' + '|'.join(escaped) + r')\b'
#     compiled = re.compile(pattern, re.IGNORECASE)
#     return [{"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in compiled.finditer(text)]

# def _detect_allcaps_orgs(text: str) -> List[Dict[str, Any]]:
#     """All‑caps words (≥2 letters) as ORG fallback."""
#     pattern = r'\b[A-Z]{2,}\b'
#     return [{"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_names_fallback(text: str) -> List[Dict[str, Any]]:
#     """Capitalized multi‑word sequences (e.g., 'John Smith') as PERSON fallback."""
#     pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
#     return [{"label": "PERSON", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# # ----------------------------------------------------------------------
# # Public detection functions
# # ----------------------------------------------------------------------
# def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
#     if not text:
#         return []
#     nlp = _get_spacy_model()
#     detected = []
#     try:
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ in {"PERSON", "ORG"}:
#                 detected.append({
#                     "label": ent.label_,
#                     "text": ent.text,
#                     "start": ent.start_char,
#                     "end": ent.end_char
#                 })
#     except Exception as e:
#         logger.exception("SpaCy processing failed")
#     return detected

# def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
#     if not text:
#         return []
#     entities = []
#     try:
#         entities.extend(_detect_emails(text))
#         entities.extend(_detect_phones(text))
#         entities.extend(_detect_cards(text))
#         entities.extend(_detect_aadhaar(text))
#         entities.extend(_detect_ids(text))
#         entities.extend(_detect_addresses(text))
#         entities.extend(_detect_common_names(text))
#         entities.extend(_detect_common_orgs(text))
#         entities.extend(_detect_allcaps_orgs(text))
#         entities.extend(_detect_names_fallback(text))
#     except Exception as e:
#         logger.exception("Regex detection failed")
#     return entities

# def deduplicate_spans(spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """Remove exact duplicates (same start, end, label)."""
#     seen = set()
#     unique = []
#     for span in spans:
#         key = (span['start'], span['end'], span['label'])
#         if key not in seen:
#             seen.add(key)
#             unique.append(span)
#     return unique

# def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     if not entities:
#         return []

#     # Validate
#     for idx, ent in enumerate(entities):
#         if not all(k in ent for k in ('label', 'start', 'end')):
#             raise ValueError(f"Entity {idx} missing required keys: {ent}")
#         if not isinstance(ent['start'], int) or not isinstance(ent['end'], int):
#             raise ValueError(f"Entity {idx} start/end must be integers: {ent}")
#         if ent['start'] < 0 or ent['end'] <= ent['start']:
#             raise ValueError(f"Entity {idx} has invalid span: {ent}")

#     # Sort: start asc, then length desc, then priority desc
#     sorted_ents = sorted(
#         entities,
#         key=lambda e: (e['start'], - (e['end'] - e['start']), -PRIORITY_MAP.get(e['label'], 0))
#     )

#     resolved = []
#     current = sorted_ents[0]

#     for next_ent in sorted_ents[1:]:
#         if next_ent['start'] < current['end']:  # overlap
#             if (next_ent['end'] - next_ent['start']) > (current['end'] - current['start']):
#                 current = next_ent
#         else:
#             resolved.append(current)
#             current = next_ent
#     resolved.append(current)

#     logger.debug("Resolved %d entities to %d", len(entities), len(resolved))
#     return resolved

# def detect_entities(raw_text: str) -> List[Dict[str, Any]]:
#     """Main entry point."""
#     if raw_text is None:
#         return []
#     if not isinstance(raw_text, str):
#         raw_text = str(raw_text)

#     if len(raw_text) > MAX_TEXT_LENGTH:
#         logger.warning("Text exceeds max length (%d chars), returning empty", MAX_TEXT_LENGTH)
#         return []

#     spacy_spans = detect_spacy_entities(raw_text)
#     regex_spans = detect_regex_entities(raw_text)

#     # Combine all spans
#     all_spans = spacy_spans + regex_spans
#     if not all_spans:
#         return []

#     all_spans = deduplicate_spans(all_spans)
#     return resolve_overlaps(all_spans)




# final code 
"""
PII entity detection module.
Combines spaCy NER and extensive regex for global PII detection:
- Names (PERSON) via spaCy + case‑insensitive common name list + capitalized fallback
- Organizations (ORG) via spaCy + common org list + all‑caps fallback
- Emails, Phones, Credit Cards, Aadhaar (India ID), generic IDs, Addresses
All regex patterns are robust and case‑insensitive where appropriate.
"""

# import re
# import logging
# from typing import List, Dict, Any, Optional

# import spacy
# from .config import MAX_TEXT_LENGTH

# logger = logging.getLogger(__name__)

# # ----------------------------------------------------------------------
# # Globals
# # ----------------------------------------------------------------------
# _nlp: Optional[spacy.Language] = None

# # Priority for overlap resolution (higher = more important)
# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ADDRESS": 3,
#     "AADHAAR": 2,
#     "CARD": 2,
#     "ID": 2,
#     "ORG": 1,
#     "PERSON": 1
# }

# # ----------------------------------------------------------------------
# # spaCy model (lazy‑loaded, NER only)
# # ----------------------------------------------------------------------
# def _get_spacy_model() -> spacy.Language:
#     global _nlp
#     if _nlp is None:
#         logger.info("Loading spaCy model 'en_core_web_sm' (NER only)")
#         try:
#             _nlp = spacy.load(
#                 "en_core_web_sm",
#                 disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]
#             )
#         except OSError:
#             logger.error("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
#             raise
#     return _nlp

# # ----------------------------------------------------------------------
# # Common name list (case‑insensitive) – covers Indian & foreign names
# # ----------------------------------------------------------------------
# COMMON_NAMES = {
#     # Common first names (male)
#     "ram", "rama", "shyam", "ravi", "kumar", "raj", "rani", "amit", "sunil",
#     "vijay", "ajay", "suresh", "mahesh", "rohit", "sharma", "ganesha", "rahul",
#     "priya", "anita", "neha", "pooja", "deepak", "vikas", "rakesh", "sita",
#     "gita", "lakshmi", "krishna", "arjun", "bharat", "karan", "arav", "vihaan",
#     "advik", "anaya", "diya", "atharv", "vivaan", "pranav", "sai", "ishaan",
#     "dhruv", "kavya", "aditi", "tanvi", "aarav", "ananya", "anika", "aryan",
#     "ishan", "mohit", "sahil", "naveen", "pawan", "manoj", "jatin", "tarun",
#     "abhishek", "ankit", "gaurav", "hitesh", "kunal", "lalit", "mayank",
#     "nilesh", "parth", "rajat", "sachin", "tushar", "umesh", "vikram",
#     "yogesh", "bhavna", "chandni", "divya", "ekta", "falguni", "geeta",
#     "hemal", "ishita", "jaya", "kajal", "kiran", "lata", "madhu", "nandini",
#     "payal", "rekha", "shanti", "tina", "urvi", "vandana", "yashoda",
#     "john", "jane", "mike", "sarah", "david", "lisa", "paul", "anna",
#     "james", "mary", "robert", "patricia", "william", "jennifer", "richard",
#     "linda", "joseph", "barbara", "thomas", "susan", "charles", "margaret",
#     "christopher", "jessica", "daniel", "emily", "matthew", "ashley",
#     "anthony", "kimberly", "donald", "sandra", "mark", "melissa", "steven",
#     "elizabeth", "andrew", "amy", "kenneth", "carol", "joshua", "michelle",
#     "kevin", "rebecca", "brian", "laura", "george", "karen", "edward",
#     "deborah", "ronald", "cynthia", "timothy", "angela", "jason", "sharon",
#     "jeffrey", "pamela", "ryan", "kathleen", "jacob", "helen", "gary",
#     "shirley", "nicholas", "emma", "eric", "carolyn", "stephen", "janet",
#     "larry", "catherine", "justin", "christine", "scott", "heather",
#     "brandon", "diane", "benjamin", "julie", "samuel", "joyce", "gregory",
#     "victoria", "alexander", "kelly", "patrick", "christina", "frank",
#     "lauren", "raymond", "frances", "jack", "martha", "henry", "judith",
#     "jerry", "cheryl", "aaron", "megan", "louis", "andrea", "charles",
#     "tiffany", "russell", "amber", "bobby", "danielle", "phillip", "abigail",
#     "mohammed", "ali", "fatima", "ahmed", "omar", "layla", "hassan", "hussain",
#     "wei", "li", "chen", "wang", "zhang", "liu", "yang", "huang", "feng",
#     "jose", "maria", "carlos", "ana", "luis", "juan", "diego", "sofia",
#     "sergei", "olga", "dmitry", "natalia", "ivan", "tatyana", "vladimir",
#     "hiroshi", "yuki", "takashi", "sakura", "kenji", "akira", "yuto",
#     "emiko", "haruto", "hinata", "himari", "ren", "souta", "mei", "yuna",
#     "kim", "lee", "park", "choi", "jung", "kang", "yoon", "lim", "han",
#     "soo", "min", "ji", "hyun", "seo", "jin", "woo", "young",
#     # Additional common surnames (can be added separately)
#     "sharma", "verma", "gupta", "kumar", "singh", "patel", "reddy", "rao",
#     "yadav", "jha", "ojha", "mishra", "dubey", "tripathi", "chaturvedi",
#     "shukla", "pandey", "thakur", "mehta", "shah", "modi", "gandhi",
#     "desai", "joshi", "kulkarni", "patil", "pawar", "more", "jadhav",
#     "gaikwad", "ingale", "bhosale", "chavan", "nikam", "kadam", "bhosle","sneha","neha",
#     "kholi","james","jacky"
# }

# # Common organization names (case‑insensitive)
# COMMON_ORGS = {
#     "google", "microsoft", "apple", "amazon", "facebook", "meta", "netflix",
#     "spotify", "twitter", "x", "linkedin", "whatsapp", "youtube", "instagram",
#     "tiktok", "snapchat", "reddit", "discord", "slack", "zoom", "teams",
#     "outlook", "gmail", "yahoo", "bing", "baidu", "yandex", "oracle", "ibm",
#     "intel", "amd", "nvidia", "samsung", "sony", "panasonic", "lg", "philips",
#     "huawei", "xiaomi", "oppo", "vivo", "oneplus", "nokia", "motorola",
#     "porsche", "ferrari", "lamborghini", "bmw", "mercedes", "audi", "toyota",
#     "honda", "ford", "chevrolet", "volkswagen", "hyundai", "kia", "tesla",
#     "adidas", "nike", "puma", "reebok", "zara", "h&m", "gucci", "prada",
#     "chanel", "louis vuitton", "hermes", "cartier", "rolex", "omega",
#     "coca-cola", "pepsi", "starbucks", "mcdonald's", "kfc", "burger king",
#     "subway", "domino's", "pizza hut", "walmart", "target", "costco",
#     "ikea", "home depot", "lowe's", "ebay", "paypal", "visa", "mastercard",
#     "american express", "discover", "jpmorgan", "goldman sachs", "morgan stanley","jp morgan chase",
#     "goldman sachs","morgan stanley","bank of america","wells fargo","american express","new york times","wall street journal","los angeles times",
#     "united nations","world health organization","international monetary fund","mcdonald's",          # already in COMMON_ORGS, but kept here for phrase matching
#     "burger king","domino's pizza","kfc","starbucks coffee","coca cola","pizza hut","louis vuitton",
#     "hermes","cartier","rolex",
# }

# # ----------------------------------------------------------------------
# # Regex detectors (private) – each returns list of entity dicts
# # ----------------------------------------------------------------------
# def _detect_emails(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     return [{"label": "EMAIL", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_phones(text: str) -> List[Dict[str, Any]]:
#     # International phone numbers (simplified but covers most)
#     patterns = [
#         r'\+\d{1,3}[-.\s]?\d{4,14}',               # +1 234 567 8900
#         r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',    # (123) 456-7890, 123-456-7890
#         r'\b\d{5}[-.\s]?\d{5}\b',                   # Indian mobile: 98765 43210
#     ]
#     combined = '|'.join(f'(?:{p})' for p in patterns)
#     compiled = re.compile(combined, re.VERBOSE)
#     return [{"label": "PHONE", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in compiled.finditer(text)]

# def _detect_cards(text: str) -> List[Dict[str, Any]]:
#     # Credit/debit card numbers (16 digits, optional spaces/hyphens)
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_aadhaar(text: str) -> List[Dict[str, Any]]:
#     # Aadhaar: 12 digits, optional spaces/hyphens after every 4 digits
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "AADHAAR", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_ids(text: str) -> List[Dict[str, Any]]:
#     # Generic IDs: sequences of 9+ digits (excluding those caught by AADHAAR/CARD)
#     pattern = r'\b\d{9,}\b'
#     return [{"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_addresses(text: str) -> List[Dict[str, Any]]:
#     # Simplified address: street number + street name (at least 3 words)
#     pattern = r'\b\d{1,5}\s+[A-Za-z]+(?:\s+[A-Za-z]+){1,4}(?:\s+(?:road|rd|street|st|avenue|ave|lane|ln|drive|dr|court|ct|plaza|way))?\b'
#     compiled = re.compile(pattern, re.IGNORECASE)
#     matches = []
#     for m in compiled.finditer(text):
#         if len(m.group()) > 10:
#             matches.append({"label": "ADDRESS", "text": m.group(), "start": m.start(), "end": m.end()})
#     return matches

# def _detect_common_names(text: str) -> List[Dict[str, Any]]:
#     """Case‑insensitive matching of common personal names."""
#     pattern = r'\b(' + '|'.join(re.escape(name) for name in COMMON_NAMES) + r')\b'
#     compiled = re.compile(pattern, re.IGNORECASE)
#     return [{"label": "PERSON", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in compiled.finditer(text)]

# def _detect_common_orgs(text: str) -> List[Dict[str, Any]]:
#     """Case‑insensitive matching of common organization names."""
#     # Escape names and join (names may contain apostrophes, dots, etc.)
#     escaped = [re.escape(name) for name in COMMON_ORGS]
#     pattern = r'\b(' + '|'.join(escaped) + r')\b'
#     compiled = re.compile(pattern, re.IGNORECASE)
#     return [{"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in compiled.finditer(text)]

# def _detect_allcaps_orgs(text: str) -> List[Dict[str, Any]]:
#     """All‑caps words (≥2 letters) as ORG fallback."""
#     pattern = r'\b[A-Z]{2,}\b'
#     return [{"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_names_fallback(text: str) -> List[Dict[str, Any]]:
#     """Capitalized multi‑word sequences (e.g., 'John Smith') as PERSON fallback."""
#     pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
#     return [{"label": "PERSON", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# # ----------------------------------------------------------------------
# # Public detection functions
# # ----------------------------------------------------------------------
# def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
#     if not text:
#         return []
#     nlp = _get_spacy_model()
#     detected = []
#     try:
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ in {"PERSON", "ORG"}:
#                 detected.append({
#                     "label": ent.label_,
#                     "text": ent.text,
#                     "start": ent.start_char,
#                     "end": ent.end_char
#                 })
#     except Exception as e:
#         logger.exception("SpaCy processing failed")
#     return detected

# def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
#     if not text:
#         return []
#     entities = []
#     try:
#         entities.extend(_detect_emails(text))
#         entities.extend(_detect_phones(text))
#         entities.extend(_detect_cards(text))
#         entities.extend(_detect_aadhaar(text))
#         entities.extend(_detect_ids(text))
#         entities.extend(_detect_addresses(text))
#         entities.extend(_detect_common_names(text))
#         entities.extend(_detect_common_orgs(text))
#         entities.extend(_detect_allcaps_orgs(text))
#         entities.extend(_detect_names_fallback(text))
#     except Exception as e:
#         logger.exception("Regex detection failed")
#     return entities

# def deduplicate_spans(spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """Remove exact duplicates (same start, end, label)."""
#     seen = set()
#     unique = []
#     for span in spans:
#         key = (span['start'], span['end'], span['label'])
#         if key not in seen:
#             seen.add(key)
#             unique.append(span)
#     return unique

# def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     if not entities:
#         return []

#     # Validate
#     for idx, ent in enumerate(entities):
#         if not all(k in ent for k in ('label', 'start', 'end')):
#             raise ValueError(f"Entity {idx} missing required keys: {ent}")
#         if not isinstance(ent['start'], int) or not isinstance(ent['end'], int):
#             raise ValueError(f"Entity {idx} start/end must be integers: {ent}")
#         if ent['start'] < 0 or ent['end'] <= ent['start']:
#             raise ValueError(f"Entity {idx} has invalid span: {ent}")

#     # Sort: start asc, then length desc, then priority desc
#     sorted_ents = sorted(
#         entities,
#         key=lambda e: (e['start'], - (e['end'] - e['start']), -PRIORITY_MAP.get(e['label'], 0))
#     )

#     resolved = []
#     current = sorted_ents[0]

#     for next_ent in sorted_ents[1:]:
#         if next_ent['start'] < current['end']:  # overlap
#             if (next_ent['end'] - next_ent['start']) > (current['end'] - current['start']):
#                 current = next_ent
#         else:
#             resolved.append(current)
#             current = next_ent
#     resolved.append(current)

#     logger.debug("Resolved %d entities to %d", len(entities), len(resolved))
#     return resolved

# def detect_entities(raw_text: str) -> List[Dict[str, Any]]:
#     """Main entry point."""
#     if raw_text is None:
#         return []
#     if not isinstance(raw_text, str):
#         raw_text = str(raw_text)

#     if len(raw_text) > MAX_TEXT_LENGTH:
#         logger.warning("Text exceeds max length (%d chars), returning empty", MAX_TEXT_LENGTH)
#         return []

#     spacy_spans = detect_spacy_entities(raw_text)
#     regex_spans = detect_regex_entities(raw_text)

#     # Combine all spans
#     all_spans = spacy_spans + regex_spans
#     if not all_spans:
#         return []

#     all_spans = deduplicate_spans(all_spans)
#     return resolve_overlaps(all_spans)


# # day 19 final change 


# import re
# import logging
# from typing import List, Dict, Any, Optional

# import spacy
# from .config import MAX_TEXT_LENGTH

# logger = logging.getLogger(__name__)

# # ----------------------------------------------------------------------
# # Globals
# # ----------------------------------------------------------------------
# _nlp: Optional[spacy.Language] = None

# # Priority for overlap resolution (higher = more important)
# PRIORITY_MAP = {
#     "EMAIL": 5,
#     "PHONE": 4,
#     "ADDRESS": 3,
#     "AADHAAR": 2,
#     "CARD": 2,
#     "ID": 2,
#     "ORG": 1,
#     "PERSON": 1
# }

# # ----------------------------------------------------------------------
# # spaCy model (lazy‑loaded, NER only)
# # ----------------------------------------------------------------------
# def _get_spacy_model() -> spacy.Language:
#     global _nlp
#     if _nlp is None:
#         logger.info("Loading spaCy model 'en_core_web_sm' (NER only)")
#         try:
#             _nlp = spacy.load(
#                 "en_core_web_sm",
#                 disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]
#             )
#         except OSError:
#             logger.error("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
#             raise
#     return _nlp

# # ----------------------------------------------------------------------
# # Common name list (case‑insensitive) – expanded
# # ----------------------------------------------------------------------
# COMMON_NAMES = {
#     # Indian names (male/female)
#     "ram", "rama", "shyam", "ravi", "kumar", "raj", "rani", "amit", "sunil",
#     "vijay", "ajay", "suresh", "mahesh", "rohit", "sharma", "ganesha", "rahul",
#     "priya", "anita", "neha", "pooja", "deepak", "vikas", "rakesh", "sita",
#     "gita", "lakshmi", "krishna", "arjun", "bharat", "karan", "arav", "vihaan",
#     "advik", "anaya", "diya", "atharv", "vivaan", "pranav", "sai", "ishaan",
#     "dhruv", "kavya", "aditi", "tanvi", "aarav", "ananya", "anika", "aryan",
#     "ishan", "mohit", "sahil", "naveen", "pawan", "manoj", "jatin", "tarun",
#     "abhishek", "ankit", "gaurav", "hitesh", "kunal", "lalit", "mayank",
#     "nilesh", "parth", "rajat", "sachin", "tushar", "umesh", "vikram",
#     "yogesh", "bhavna", "chandni", "divya", "ekta", "falguni", "geeta",
#     "hemal", "ishita", "jaya", "kajal", "kiran", "lata", "madhu", "nandini",
#     "payal", "rekha", "shanti", "tina", "urvi", "vandana", "yashoda",
#     "sneha", "sejal",                 # added
#     # Western names
#     "john", "jane", "mike", "sarah", "david", "lisa", "paul", "anna",
#     "james", "mary", "robert", "patricia", "william", "jennifer", "richard",
#     "linda", "joseph", "barbara", "thomas", "susan", "charles", "margaret",
#     "christopher", "jessica", "daniel", "emily", "matthew", "ashley",
#     "anthony", "kimberly", "donald", "sandra", "mark", "melissa", "steven",
#     "elizabeth", "andrew", "amy", "kenneth", "carol", "joshua", "michelle",
#     "kevin", "rebecca", "brian", "laura", "george", "karen", "edward",
#     "deborah", "ronald", "cynthia", "timothy", "angela", "jason", "sharon",
#     "jeffrey", "pamela", "ryan", "kathleen", "jacob", "helen", "gary",
#     "shirley", "nicholas", "emma", "eric", "carolyn", "stephen", "janet",
#     "larry", "catherine", "justin", "christine", "scott", "heather",
#     "brandon", "diane", "benjamin", "julie", "samuel", "joyce", "gregory",
#     "victoria", "alexander", "kelly", "patrick", "christina", "frank",
#     "lauren", "raymond", "frances", "jack", "martha", "henry", "judith",
#     "jerry", "cheryl", "aaron", "megan", "louis", "andrea", "charles",
#     "tiffany", "russell", "amber", "bobby", "danielle", "phillip", "abigail",
#     # Additional global names
#     "mohammed", "ali", "fatima", "ahmed", "omar", "layla", "hassan", "hussain",
#     "wei", "li", "chen", "wang", "zhang", "liu", "yang", "huang", "feng",
#     "jose", "maria", "carlos", "ana", "luis", "juan", "diego", "sofia",
#     "sergei", "olga", "dmitry", "natalia", "ivan", "tatyana", "vladimir",
#     "hiroshi", "yuki", "takashi", "sakura", "kenji", "akira", "yuto",
#     "emiko", "haruto", "hinata", "himari", "ren", "souta", "mei", "yuna",
#     "kim", "lee", "park", "choi", "jung", "kang", "yoon", "lim", "han",
#     "soo", "min", "ji", "hyun", "seo", "jin", "woo", "young",
#     # Surnames
#     "sharma", "verma", "gupta", "kumar", "singh", "patel", "reddy", "rao",
#     "yadav", "jha", "ojha", "mishra", "dubey", "tripathi", "chaturvedi",
#     "shukla", "pandey", "thakur", "mehta", "shah", "modi", "gandhi",
#     "desai", "joshi", "kulkarni", "patil", "pawar", "more", "jadhav",
#     "gaikwad", "ingale", "bhosale", "chavan", "nikam", "kadam", "bhosle",
#     "kholi", "james", "jacky"
# }

# # ----------------------------------------------------------------------
# # Single‑word organization names (case‑insensitive)
# # ----------------------------------------------------------------------
# SINGLE_WORD_ORGS = {
#     "google", "microsoft", "apple", "amazon", "facebook", "meta", "netflix",
#     "spotify", "twitter", "x", "linkedin", "whatsapp", "youtube", "instagram",
#     "tiktok", "snapchat", "reddit", "discord", "slack", "zoom", "teams",
#     "outlook", "gmail", "yahoo", "bing", "baidu", "yandex", "oracle", "ibm",
#     "intel", "amd", "nvidia", "samsung", "sony", "panasonic", "lg", "philips",
#     "huawei", "xiaomi", "oppo", "vivo", "oneplus", "nokia", "motorola",
#     "porsche", "ferrari", "lamborghini", "bmw", "mercedes", "audi", "toyota",
#     "honda", "ford", "chevrolet", "volkswagen", "hyundai", "kia", "tesla",
#     "adidas", "nike", "puma", "reebok", "zara", "h&m", "gucci", "prada",
#     "chanel", "hermes", "cartier", "rolex", "omega",
#     "mcdonald's", "kfc", "subway", "ebay", "paypal", "visa", "mastercard",
#     "discover", "jpmorgan", "mcdonald's", "starbucks", "domino's"
# }

# # ----------------------------------------------------------------------
# # Multi‑word organization names (case‑insensitive) – detected as whole phrases
# # ----------------------------------------------------------------------
# MULTI_WORD_ORGS = {
#     "american express",
#     "jp morgan chase",
#     "goldman sachs",
#     "morgan stanley",
#     "bank of america",
#     "wells fargo",
#     "new york times",
#     "wall street journal",
#     "los angeles times",
#     "united nations",
#     "world health organization",
#     "international monetary fund",
#     "burger king",
#     "domino's pizza",
#     "starbucks coffee",
#     "coca cola",
#     "pizza hut",
#     "louis vuitton"
# }

# # ----------------------------------------------------------------------
# # Regex detectors (private)
# # ----------------------------------------------------------------------
# def _detect_emails(text: str) -> List[Dict[str, Any]]:
#     pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
#     return [{"label": "EMAIL", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_phones(text: str) -> List[Dict[str, Any]]:
#     # International phone numbers (simplified but covers most)
#     patterns = [
#         r'\+\d{1,3}[-.\s]?\d{4,14}',               # +1 234 567 8900
#         r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',    # (123) 456-7890, 123-456-7890
#         r'\b\d{5}[-.\s]?\d{5}\b',                   # Indian mobile: 98765 43210
#     ]
#     combined = '|'.join(f'(?:{p})' for p in patterns)
#     compiled = re.compile(combined, re.VERBOSE)
#     return [{"label": "PHONE", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in compiled.finditer(text)]

# def _detect_cards(text: str) -> List[Dict[str, Any]]:
#     # Credit/debit card numbers (16 digits, optional spaces/hyphens)
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_aadhaar(text: str) -> List[Dict[str, Any]]:
#     # Aadhaar: 12 digits, optional spaces/hyphens after every 4 digits
#     pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
#     return [{"label": "AADHAAR", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_ids(text: str) -> List[Dict[str, Any]]:
#     # Generic IDs: sequences of 9+ digits (excluding those caught by AADHAAR/CARD)
#     pattern = r'\b\d{9,}\b'
#     return [{"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_addresses(text: str) -> List[Dict[str, Any]]:
#     # Simplified address: street number + street name (at least 3 words)
#     pattern = r'\b\d{1,5}\s+[A-Za-z]+(?:\s+[A-Za-z]+){1,4}(?:\s+(?:road|rd|street|st|avenue|ave|lane|ln|drive|dr|court|ct|plaza|way))?\b'
#     compiled = re.compile(pattern, re.IGNORECASE)
#     matches = []
#     for m in compiled.finditer(text):
#         if len(m.group()) > 10:
#             matches.append({"label": "ADDRESS", "text": m.group(), "start": m.start(), "end": m.end()})
#     return matches

# def _detect_common_names(text: str) -> List[Dict[str, Any]]:
#     """Case‑insensitive matching of common personal names."""
#     pattern = r'\b(' + '|'.join(re.escape(name) for name in COMMON_NAMES) + r')\b'
#     compiled = re.compile(pattern, re.IGNORECASE)
#     return [{"label": "PERSON", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in compiled.finditer(text)]

# def _detect_single_word_orgs(text: str) -> List[Dict[str, Any]]:
#     """Match single‑word organization names."""
#     pattern = r'\b(' + '|'.join(re.escape(name) for name in SINGLE_WORD_ORGS) + r')\b'
#     compiled = re.compile(pattern, re.IGNORECASE)
#     return [{"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in compiled.finditer(text)]

# def _detect_multi_word_orgs(text: str) -> List[Dict[str, Any]]:
#     """Match multi‑word organization phrases exactly."""
#     pattern = r'\b(' + '|'.join(re.escape(phrase) for phrase in MULTI_WORD_ORGS) + r')\b'
#     compiled = re.compile(pattern, re.IGNORECASE)
#     return [{"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in compiled.finditer(text)]

# def _detect_allcaps_orgs(text: str) -> List[Dict[str, Any]]:
#     """All‑caps words (≥2 letters) as ORG fallback."""
#     pattern = r'\b[A-Z]{2,}\b'
#     return [{"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# def _detect_names_fallback(text: str) -> List[Dict[str, Any]]:
#     """Capitalized multi‑word sequences (e.g., 'John Smith') as PERSON fallback."""
#     pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
#     return [{"label": "PERSON", "text": m.group(), "start": m.start(), "end": m.end()}
#             for m in re.finditer(pattern, text)]

# # ----------------------------------------------------------------------
# # Public detection functions
# # ----------------------------------------------------------------------
# def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
#     if not text:
#         return []
#     nlp = _get_spacy_model()
#     detected = []
#     try:
#         doc = nlp(text)
#         for ent in doc.ents:
#             if ent.label_ in {"PERSON", "ORG"}:
#                 detected.append({
#                     "label": ent.label_,
#                     "text": ent.text,
#                     "start": ent.start_char,
#                     "end": ent.end_char
#                 })
#     except Exception as e:
#         logger.exception("SpaCy processing failed")
#     return detected

# def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
#     if not text:
#         return []
#     entities = []
#     try:
#         entities.extend(_detect_emails(text))
#         entities.extend(_detect_phones(text))
#         entities.extend(_detect_cards(text))
#         entities.extend(_detect_aadhaar(text))
#         entities.extend(_detect_ids(text))
#         entities.extend(_detect_addresses(text))
#         entities.extend(_detect_common_names(text))
#         entities.extend(_detect_single_word_orgs(text))
#         entities.extend(_detect_multi_word_orgs(text))
#         entities.extend(_detect_allcaps_orgs(text))
#         entities.extend(_detect_names_fallback(text))
#     except Exception as e:
#         logger.exception("Regex detection failed")
#     return entities

# def deduplicate_spans(spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """Remove exact duplicates (same start, end, label)."""
#     seen = set()
#     unique = []
#     for span in spans:
#         key = (span['start'], span['end'], span['label'])
#         if key not in seen:
#             seen.add(key)
#             unique.append(span)
#     return unique

# def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     if not entities:
#         return []

#     # Validate
#     for idx, ent in enumerate(entities):
#         if not all(k in ent for k in ('label', 'start', 'end')):
#             raise ValueError(f"Entity {idx} missing required keys: {ent}")
#         if not isinstance(ent['start'], int) or not isinstance(ent['end'], int):
#             raise ValueError(f"Entity {idx} start/end must be integers: {ent}")
#         if ent['start'] < 0 or ent['end'] <= ent['start']:
#             raise ValueError(f"Entity {idx} has invalid span: {ent}")

#     # Sort: start asc, then length desc, then priority desc
#     sorted_ents = sorted(
#         entities,
#         key=lambda e: (e['start'], - (e['end'] - e['start']), -PRIORITY_MAP.get(e['label'], 0))
#     )

#     resolved = []
#     current = sorted_ents[0]

#     for next_ent in sorted_ents[1:]:
#         if next_ent['start'] < current['end']:  # overlap
#             if (next_ent['end'] - next_ent['start']) > (current['end'] - current['start']):
#                 current = next_ent
#         else:
#             resolved.append(current)
#             current = next_ent
#     resolved.append(current)

#     logger.debug("Resolved %d entities to %d", len(entities), len(resolved))
#     return resolved

# def detect_entities(raw_text: str) -> List[Dict[str, Any]]:
#     """Main entry point."""
#     if raw_text is None:
#         return []
#     if not isinstance(raw_text, str):
#         raw_text = str(raw_text)

#     if len(raw_text) > MAX_TEXT_LENGTH:
#         logger.warning("Text exceeds max length (%d chars), returning empty", MAX_TEXT_LENGTH)
#         return []

#     spacy_spans = detect_spacy_entities(raw_text)
#     regex_spans = detect_regex_entities(raw_text)

#     # Combine all spans
#     all_spans = spacy_spans + regex_spans
#     if not all_spans:
#         return []

#     all_spans = deduplicate_spans(all_spans)
#     return resolve_overlaps(all_spans)



# day 19 final code 

import re
import logging
from typing import List, Dict, Any, Optional

import spacy
from .config import MAX_TEXT_LENGTH

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Globals
# ----------------------------------------------------------------------
_nlp: Optional[spacy.Language] = None

# Priority for overlap resolution (higher = more important)
PRIORITY_MAP = {
    "EMAIL": 5,
    "PHONE": 4,
    "ADDRESS": 3,
    "AADHAAR": 2,
    "CARD": 2,
    "ID": 2,
    "ORG": 1,
    "PERSON": 1
}

# ----------------------------------------------------------------------
# spaCy model (lazy‑loaded, NER only)
# ----------------------------------------------------------------------
def _get_spacy_model() -> spacy.Language:
    global _nlp
    if _nlp is None:
        logger.info("Loading spaCy model 'en_core_web_sm' (NER only)")
        try:
            _nlp = spacy.load(
                "en_core_web_sm",
                disable=["tagger", "parser", "attribute_ruler", "lemmatizer"]
            )
        except OSError:
            logger.error("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
            raise
    return _nlp

# ----------------------------------------------------------------------
# Common name list (case‑insensitive) – expanded
# ----------------------------------------------------------------------
COMMON_NAMES = {
    # Indian names
    "ram", "rama", "shyam", "ravi", "kumar", "raj", "rani", "amit", "sunil",
    "vijay", "ajay", "suresh", "mahesh", "rohit", "sharma", "ganesha", "rahul",
    "priya", "anita", "neha", "pooja", "deepak", "vikas", "rakesh", "sita",
    "gita", "lakshmi", "krishna", "arjun", "bharat", "karan", "arav", "vihaan",
    "advik", "anaya", "diya", "atharv", "vivaan", "pranav", "sai", "ishaan",
    "dhruv", "kavya", "aditi", "tanvi", "aarav", "ananya", "anika", "aryan",
    "ishan", "mohit", "sahil", "naveen", "pawan", "manoj", "jatin", "tarun",
    "abhishek", "ankit", "gaurav", "hitesh", "kunal", "lalit", "mayank",
    "nilesh", "parth", "rajat", "sachin", "tushar", "umesh", "vikram",
    "yogesh", "bhavna", "chandni", "divya", "ekta", "falguni", "geeta",
    "hemal", "ishita", "jaya", "kajal", "kiran", "lata", "madhu", "nandini",
    "payal", "rekha", "shanti", "tina", "urvi", "vandana", "yashoda",
    "sneha", "sejal",
    # Western names
    "john", "jane", "mike", "sarah", "david", "lisa", "paul", "anna",
    "james", "mary", "robert", "patricia", "william", "jennifer", "richard",
    "linda", "joseph", "barbara", "thomas", "susan", "charles", "margaret",
    "christopher", "jessica", "daniel", "emily", "matthew", "ashley",
    "anthony", "kimberly", "donald", "sandra", "mark", "melissa", "steven",
    "elizabeth", "andrew", "amy", "kenneth", "carol", "joshua", "michelle",
    "kevin", "rebecca", "brian", "laura", "george", "karen", "edward",
    "deborah", "ronald", "cynthia", "timothy", "angela", "jason", "sharon",
    "jeffrey", "pamela", "ryan", "kathleen", "jacob", "helen", "gary",
    "shirley", "nicholas", "emma", "eric", "carolyn", "stephen", "janet",
    "larry", "catherine", "justin", "christine", "scott", "heather",
    "brandon", "diane", "benjamin", "julie", "samuel", "joyce", "gregory",
    "victoria", "alexander", "kelly", "patrick", "christina", "frank",
    "lauren", "raymond", "frances", "jack", "martha", "henry", "judith",
    "jerry", "cheryl", "aaron", "megan", "louis", "andrea", "charles",
    "tiffany", "russell", "amber", "bobby", "danielle", "phillip", "abigail",
    # Additional global names
    "mohammed", "ali", "fatima", "ahmed", "omar", "layla", "hassan", "hussain",
    "wei", "li", "chen", "wang", "zhang", "liu", "yang", "huang", "feng",
    "jose", "maria", "carlos", "ana", "luis", "juan", "diego", "sofia",
    "sergei", "olga", "dmitry", "natalia", "ivan", "tatyana", "vladimir",
    "hiroshi", "yuki", "takashi", "sakura", "kenji", "akira", "yuto",
    "emiko", "haruto", "hinata", "himari", "ren", "souta", "mei", "yuna",
    "kim", "lee", "park", "choi", "jung", "kang", "yoon", "lim", "han",
    "soo", "min", "ji", "hyun", "seo", "jin", "woo", "young",
    # Surnames
    "sharma", "verma", "gupta", "kumar", "singh", "patel", "reddy", "rao",
    "yadav", "jha", "ojha", "mishra", "dubey", "tripathi", "chaturvedi",
    "shukla", "pandey", "thakur", "mehta", "shah", "modi", "gandhi",
    "desai", "joshi", "kulkarni", "patil", "pawar", "more", "jadhav",
    "gaikwad", "ingale", "bhosale", "chavan", "nikam", "kadam", "bhosle",
    "kholi", "james", "jacky"
}

# ----------------------------------------------------------------------
# Single‑word organization names (case‑insensitive)
# ----------------------------------------------------------------------
SINGLE_WORD_ORGS = {
    "google", "microsoft", "apple", "amazon", "facebook", "meta", "netflix",
    "spotify", "twitter", "x", "linkedin", "whatsapp", "youtube", "instagram",
    "tiktok", "snapchat", "reddit", "discord", "slack", "zoom", "teams",
    "outlook", "gmail", "yahoo", "bing", "baidu", "yandex", "oracle", "ibm",
    "intel", "amd", "nvidia", "samsung", "sony", "panasonic", "lg", "philips",
    "huawei", "xiaomi", "oppo", "vivo", "oneplus", "nokia", "motorola",
    "porsche", "ferrari", "lamborghini", "bmw", "mercedes", "audi", "toyota",
    "honda", "ford", "chevrolet", "volkswagen", "hyundai", "kia", "tesla",
    "adidas", "nike", "puma", "reebok", "zara", "h&m", "gucci", "prada",
    "chanel", "hermes", "cartier", "rolex", "omega",
    "mcdonald's", "kfc", "subway", "ebay", "paypal", "visa", "mastercard",
    "discover", "jpmorgan", "starbucks", "domino's"
}

# ----------------------------------------------------------------------
# Multi‑word organization names (case‑insensitive) – detected as whole phrases
# ----------------------------------------------------------------------
MULTI_WORD_ORGS = {
    "american express",
    "jp morgan chase",
    "goldman sachs",
    "morgan stanley",
    "bank of america",
    "wells fargo",
    "new york times",
    "wall street journal",
    "los angeles times",
    "united nations",
    "world health organization",
    "international monetary fund",
    "burger king",
    "domino's pizza",
    "starbucks coffee",
    "coca cola",
    "pizza hut",
    "louis vuitton"
}

# ----------------------------------------------------------------------
# Regex detectors (private)
# ----------------------------------------------------------------------
def _detect_emails(text: str) -> List[Dict[str, Any]]:
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    return [{"label": "EMAIL", "text": m.group(), "start": m.start(), "end": m.end()}
            for m in re.finditer(pattern, text)]

def _detect_phones(text: str) -> List[Dict[str, Any]]:
    patterns = [
        r'\+\d{1,3}[-.\s]?\d{4,14}',               # +1 234 567 8900
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',    # (123) 456-7890, 123-456-7890
        r'\b\d{5}[-.\s]?\d{5}\b',                   # Indian mobile: 98765 43210
    ]
    combined = '|'.join(f'(?:{p})' for p in patterns)
    compiled = re.compile(combined, re.VERBOSE)
    return [{"label": "PHONE", "text": m.group(), "start": m.start(), "end": m.end()}
            for m in compiled.finditer(text)]

def _detect_cards(text: str) -> List[Dict[str, Any]]:
    pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    return [{"label": "CARD", "text": m.group(), "start": m.start(), "end": m.end()}
            for m in re.finditer(pattern, text)]

def _detect_aadhaar(text: str) -> List[Dict[str, Any]]:
    pattern = r'\b\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    return [{"label": "AADHAAR", "text": m.group(), "start": m.start(), "end": m.end()}
            for m in re.finditer(pattern, text)]

def _detect_ids(text: str) -> List[Dict[str, Any]]:
    pattern = r'\b\d{9,}\b'
    return [{"label": "ID", "text": m.group(), "start": m.start(), "end": m.end()}
            for m in re.finditer(pattern, text)]

def _detect_addresses(text: str) -> List[Dict[str, Any]]:
    pattern = r'\b\d{1,5}\s+[A-Za-z]+(?:\s+[A-Za-z]+){1,4}(?:\s+(?:road|rd|street|st|avenue|ave|lane|ln|drive|dr|court|ct|plaza|way))?\b'
    compiled = re.compile(pattern, re.IGNORECASE)
    matches = []
    for m in compiled.finditer(text):
        if len(m.group()) > 10:
            matches.append({"label": "ADDRESS", "text": m.group(), "start": m.start(), "end": m.end()})
    return matches

def _detect_common_names(text: str) -> List[Dict[str, Any]]:
    pattern = r'\b(' + '|'.join(re.escape(name) for name in COMMON_NAMES) + r')\b'
    compiled = re.compile(pattern, re.IGNORECASE)
    return [{"label": "PERSON", "text": m.group(), "start": m.start(), "end": m.end()}
            for m in compiled.finditer(text)]

def _detect_single_word_orgs(text: str) -> List[Dict[str, Any]]:
    pattern = r'\b(' + '|'.join(re.escape(name) for name in SINGLE_WORD_ORGS) + r')\b'
    compiled = re.compile(pattern, re.IGNORECASE)
    return [{"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
            for m in compiled.finditer(text)]

def _detect_multi_word_orgs(text: str) -> List[Dict[str, Any]]:
    pattern = r'\b(' + '|'.join(re.escape(phrase) for phrase in MULTI_WORD_ORGS) + r')\b'
    compiled = re.compile(pattern, re.IGNORECASE)
    return [{"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
            for m in compiled.finditer(text)]

def _detect_allcaps_orgs(text: str) -> List[Dict[str, Any]]:
    pattern = r'\b[A-Z]{2,}\b'
    return [{"label": "ORG", "text": m.group(), "start": m.start(), "end": m.end()}
            for m in re.finditer(pattern, text)]

def _detect_names_fallback(text: str) -> List[Dict[str, Any]]:
    pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
    return [{"label": "PERSON", "text": m.group(), "start": m.start(), "end": m.end()}
            for m in re.finditer(pattern, text)]

# ----------------------------------------------------------------------
# Public detection functions
# ----------------------------------------------------------------------
def detect_spacy_entities(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []
    nlp = _get_spacy_model()
    detected = []
    try:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in {"PERSON", "ORG"}:
                detected.append({
                    "label": ent.label_,
                    "text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
    except Exception as e:
        logger.exception("SpaCy processing failed")
    return detected

def detect_regex_entities(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []
    entities = []
    try:
        entities.extend(_detect_emails(text))
        entities.extend(_detect_phones(text))
        entities.extend(_detect_cards(text))
        entities.extend(_detect_aadhaar(text))
        entities.extend(_detect_ids(text))
        entities.extend(_detect_addresses(text))
        entities.extend(_detect_common_names(text))
        entities.extend(_detect_single_word_orgs(text))
        entities.extend(_detect_multi_word_orgs(text))
        entities.extend(_detect_allcaps_orgs(text))
        entities.extend(_detect_names_fallback(text))
    except Exception as e:
        logger.exception("Regex detection failed")
    return entities

def deduplicate_spans(spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    unique = []
    for span in spans:
        key = (span['start'], span['end'], span['label'])
        if key not in seen:
            seen.add(key)
            unique.append(span)
    return unique

def resolve_overlaps(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not entities:
        return []

    for idx, ent in enumerate(entities):
        if not all(k in ent for k in ('label', 'start', 'end')):
            raise ValueError(f"Entity {idx} missing required keys: {ent}")
        if not isinstance(ent['start'], int) or not isinstance(ent['end'], int):
            raise ValueError(f"Entity {idx} start/end must be integers: {ent}")
        if ent['start'] < 0 or ent['end'] <= ent['start']:
            raise ValueError(f"Entity {idx} has invalid span: {ent}")

    sorted_ents = sorted(
        entities,
        key=lambda e: (e['start'], - (e['end'] - e['start']), -PRIORITY_MAP.get(e['label'], 0))
    )

    resolved = []
    current = sorted_ents[0]

    for next_ent in sorted_ents[1:]:
        if next_ent['start'] < current['end']:
            if (next_ent['end'] - next_ent['start']) > (current['end'] - current['start']):
                current = next_ent
        else:
            resolved.append(current)
            current = next_ent
    resolved.append(current)

    logger.debug("Resolved %d entities to %d", len(entities), len(resolved))
    return resolved

def detect_entities(raw_text: str) -> List[Dict[str, Any]]:
    if raw_text is None:
        return []
    if not isinstance(raw_text, str):
        raw_text = str(raw_text)

    if len(raw_text) > MAX_TEXT_LENGTH:
        logger.warning("Text exceeds max length (%d chars), returning empty", MAX_TEXT_LENGTH)
        return []

    spacy_spans = detect_spacy_entities(raw_text)
    regex_spans = detect_regex_entities(raw_text)

    all_spans = spacy_spans + regex_spans
    if not all_spans:
        return []

    all_spans = deduplicate_spans(all_spans)
    return resolve_overlaps(all_spans)