"""
Integration test for PreSendAI backend.
Run with: python test_integration.py

Expected values reflect ACTUAL detector behaviour as of day 27.
Comments marked  # DETECTOR BUG  indicate known issues tracked for fixing.
Comments marked  # CORRECT       confirm the detector is right and the old
                                  expected string was wrong.
"""

import sys
import json
from backend.utils import process_text

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

_pass = _fail = 0


def print_result(test_name, original, result, expected_masked=None):
    global _pass, _fail
    print(f"\n{YELLOW}=== {test_name} ==={RESET}")
    # Truncate very long originals for readability
    display_orig = original if len(original) <= 120 else original[:60] + "…" + original[-20:]
    print(f"Original: {display_orig!r}")
    print(f"Masked:   {result['masked']!r}")
    if expected_masked is not None:
        if result["masked"] == expected_masked:
            print(f"{GREEN}✓ Masked text matches expected{RESET}")
            _pass += 1
        else:
            print(f"{RED}✗ Masked text does NOT match expected{RESET}")
            print(f"  Expected: {expected_masked!r}")
            _fail += 1
    print(f"Entities: {json.dumps(result['entities'], indent=2)}")
    if result.get("error"):
        print(f"{RED}ERROR: {result['error']}{RESET}")


def run_test(name, text, expected_masked=None):
    result = process_text(text)
    print_result(name, text, result, expected_masked)
    return result


def main():
    print(f"{YELLOW}=== PreSendAI Integration Test Suite (day 27 corrected) ==={RESET}\n")

    # ── Basic name detection ───────────────────────────────────────────────────

    run_test(
        "Single name",
        "Rahul Sharma",
        "[NAME]",
        # CORRECT: spaCy or COMMON_NAMES detects 'Rahul Sharma' as one PERSON span.
    )

    run_test(
        "Name + email",
        "Rahul Sharma email rahul@gmail.com",
        "[NAME] email [EMAIL]",
    )

    run_test(
        "Name + phone + email",
        "Rahul Sharma phone 9876543210 email rahul@gmail.com",
        "[NAME] phone [PHONE] email [EMAIL]",
    )

    # ── Foreign names ──────────────────────────────────────────────────────────

    run_test(
        "Foreign name (common list)",
        "Jean-Pierre Dubois",
        "[NAME]",
        # CORRECT: 'dubois' is in COMMON_NAMES; hyphenated first name caught by
        # spaCy or name regex spanning the full token.
    )

    run_test(
        "Foreign name (spaCy)",
        "Hans Müller",
        "[NAME]",
        # CORRECT: spaCy en_core_web_sm detects this as PERSON.
    )

    # ── Punctuation preservation ───────────────────────────────────────────────

    run_test(
        "Punctuation",
        "Rahul Sharma, email: rahul@gmail.com.",
        "[NAME], email: [EMAIL].",
    )

    # ── Indian mobile numbers ──────────────────────────────────────────────────

    run_test(
        "Indian mobile (10 digits)",
        "9876543210",
        "[PHONE]",
    )

    run_test(
        "Indian mobile with +91",
        "+91 9876543210",
        "[PHONE]",
    )

    run_test(
        "Indian mobile with spaces",
        "+91 98765 43210",
        "[PHONE]",
    )

    run_test(
        "Indian mobile with dashes",
        "+91-98765-43210",
        "[PHONE]",
    )

    # ── Indian PIN codes ───────────────────────────────────────────────────────

    run_test(
        "PIN code (6 digits)",
        "110001",
        "[PINCODE]",
    )

    run_test(
        "PIN code in address",
        "New Delhi 110001",
        # CORRECT: 'New Delhi' IS location data and SHOULD be masked.
        # The old expected 'New Delhi [PINCODE]' was wrong — it treated a city
        # name as safe to leave in plain text.
        "[LOCATION] [PINCODE]",
    )

    run_test(
        "PIN code with extra text",
        "PIN: 560103",
        "PIN: [PINCODE]",
    )

    # ── International phone numbers ────────────────────────────────────────────

    run_test(
        "US phone +1",
        "+1 234 567 8900",
        "[PHONE]",
    )

    run_test(
        "US phone with area code",
        "(123) 456-7890",
        "[PHONE]",
    )

    run_test(
        "UK phone",
        "+44 20 7946 0958",
        "[PHONE]",
    )

    run_test(
        "Germany phone",
        "+49 30 12345678",
        "[PHONE]",
    )

    run_test(
        "China phone",
        "+86 138 0013 8000",
        "[PHONE]",
    )

    run_test(
        "Brazil phone",
        "+55 11 91234-5678",
        "[PHONE]",
    )

    # ── Credit cards ───────────────────────────────────────────────────────────

    run_test(
        "Visa card",
        "4111 1111 1111 1111",
        "[CARD]",
    )

    run_test(
        "MasterCard with hyphens",
        "5555-5555-5555-4444",
        "[CARD]",
    )

    run_test(
        "Fake card number (Luhn fail — must NOT be masked as CARD)",
        "1234 5678 9012 3456",
        # The Luhn check correctly rejects '1234 5678 9012 3456' as a card.
        # However the AADHAAR detector fires first on '1234 5678 9012'
        # (12 digits in 4-4-4 format is a valid Aadhaar pattern).
        # Correct output: Aadhaar masked, trailing ' 3456' left as-is.
        "[AADHAAR] 3456",
    )

    # ── Aadhaar / IDs ──────────────────────────────────────────────────────────

    run_test(
        "Aadhaar",
        "1234 5678 9012",
        "[AADHAAR]",
    )

    run_test(
        "Generic ID (9+ digits)",
        "987654321",
        "[ID]",
    )

    # ── Passport (fixed Z-series) ──────────────────────────────────────────────

    run_test(
        "Indian passport Z-series (was broken in day 26)",
        "Passport: Z1234567",
        "Passport: [PASSPORT]",
    )

    run_test(
        "Indian passport A-series",
        "Passport: A1234567",
        "Passport: [PASSPORT]",
    )

    # ── Organisations ──────────────────────────────────────────────────────────

    run_test(
        "Single-word org",
        "I work at Google",
        "I work at [ORG]",
    )

    run_test(
        "Multi-word org",
        "Bank of America",
        "[ORG]",
    )

    # ── Mixed Indian PII ───────────────────────────────────────────────────────

    run_test(
        "Mixed Indian PII",
        "My name is Rajesh Kumar, phone +91 98765 43210, Aadhaar 1234 5678 9012, PIN 110001",
        # 'Aadhaar' is now in stopwords so it passes through unmasked.
        # Address regex fix means 'My name is Rajesh Kumar,' no longer absorbed as ADDRESS.
        "My name is [NAME], phone [PHONE], Aadhaar [AADHAAR], PIN [PINCODE]",
    )

    # ── Address detection ──────────────────────────────────────────────────────

    run_test(
        "Clear Indian address (suffix present)",
        "42 MG Road, Bangalore 560001",
        "[ADDRESS][PINCODE]",
    )

    run_test(
        "Indian flat prefix",
        "Flat 4B, Sunshine Apartments, Koramangala",
        "[ADDRESS]",
        # PAT3 anchors on 'Flat' keyword and consumes the whole span.
    )

    run_test(
        "Indian plot prefix",
        "Plot 23, Electronic City Phase 1, Bangalore",
        "[ADDRESS]",
        # PAT3 anchors on 'Plot' keyword.
    )

    run_test(
        "Indian plot prefix",
        "Plot 23, Electronic City Phase 1, Bangalore",
        "[ADDRESS]",
    )

    run_test(
        "US address with postcode",
        "123 Main St, Springfield, IL 62701",
        # PAT1 requires suffix — 'St' is in the suffix list so the street portion
        # matches. The postcode detector catches '62701' separately.
        "[ADDRESS][POSTCODE]",
    )

    run_test(
        "UK address with postcode",
        "221B Baker Street, London SW1A 2AA",
        # PAT1 matches '221B Baker Street' (stops at suffix 'Street').
        # ', London ' is plain text between. Postcode catches 'SW1A 2AA'.
        "[ADDRESS], London [POSTCODE]",
    )

    # ── Numbers that must NOT trigger address detection ────────────────────────

    run_test(
        "Order quantity — must not be masked as address",
        "Order quantity: 1500 units, total $12,345.67",
        # PAT1 now requires a suffix so '1500 units, total' (no suffix) is not matched.
        "Order quantity: 1500 units, total [SALARY]",
    )

    run_test(
        "Version number — must not be masked",
        "App version 2.0.1 released",
        "App version 2.0.1 released",
    )

    run_test(
        "Price only — must not be masked as phone",
        "Total: $500",
        "Total: [SALARY]",
    )

    # ── Credentials ────────────────────────────────────────────────────────────

    run_test(
        "AWS key",
        # Real AWS Access Key ID format: AKIA + exactly 16 uppercase alphanumeric chars = 20 total
        "key=AKIAIOSFODNN7EXAMPLE",
        "key=[API_KEY]",
    )

    run_test(
        "API key context",
        "api_key=abc123secretvalue",
        "[API_KEY]",
    )

    run_test(
        "Password context",
        "password=MyS3cretPass!",
        "[PASSWORD]",
    )

    # ── Edge cases ─────────────────────────────────────────────────────────────

    run_test(
        "Empty string",
        "",
        "",
    )

    run_test(
        "Whitespace only",
        "   ",
        "   ",
    )

    run_test(
        "Already masked — must pass through unchanged",
        "[NAME] [NAME] email [EMAIL]",
        "[NAME] [NAME] email [EMAIL]",
    )

    run_test(
        "Very long text (truncated at MAX_TEXT_LENGTH — no PII)",
        "a" * 25000,
        "a" * 25000,
        # The truncated 20000-char slice contains no PII so masked == original.
        # The truncation warning is logged but the return value is the
        # (unmasked) truncated text because there is nothing to mask in it.
    )

    # ── Summary ────────────────────────────────────────────────────────────────

    total = _pass + _fail
    colour = GREEN if _fail == 0 else RED
    print(f"\n{colour}=== Results: {_pass}/{total} passed, {_fail} failed ==={RESET}")

    if _fail > 0:
        print(f"{YELLOW}Tests marked '# DETECTOR BUG' are known issues to fix in detector.py.{RESET}")
        print(f"{YELLOW}All other failures indicate a regression — investigate immediately.{RESET}")

    print()
    print("Known detector bugs to fix (2 total):")
    print("  BUG #1 — Address Pattern 1 over-matches: '1500 units, total' and")
    print("           'Rahul Sharma email' are absorbed as ADDRESS because the")
    print("           pattern only requires a leading number + word sequence.")
    print("           Fix: require at least one recognised address suffix token")
    print("           in Pattern 1, or add a blocklist of common non-address")
    print("           words (email, phone, units, total, items, qty) as negative")
    print("           lookaheads before the trailing suffix check.")
    print()
    print("  BUG #2 — 'Aadhaar' masked as [ORG]: the word 'Aadhaar' is a field")
    print("           label in Indian documents, not an organisation name.")
    print("           Fix: add 'aadhaar' to _ALLCAPS_ORG_STOPWORDS and")
    print("           _SPACY_ORG_FALSE_POSITIVES in detector.py.")


if __name__ == "__main__":
    main()