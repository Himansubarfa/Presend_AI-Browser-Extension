# tests/generate_dataset.py
"""Generate synthetic PII dataset for training/evaluation."""
import json
import random
import sys
import os
from faker import Faker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.detector import detect_entities

# Initialize fakers
fake = Faker('en_IN')
fake_us = Faker('en_US')

def generate_aadhaar():
    return ' '.join([''.join([str(random.randint(0, 9)) for _ in range(4)]) for _ in range(3)])

def generate_pan():
    letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))
    digits = ''.join(random.choices('0123456789', k=4))
    last = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    return letters + digits + last

def generate_phone():
    return f"+91 {random.randint(6000000000, 9999999999)}"

def generate_email(name=None):
    if name is None:
        name = fake.name() if random.random() < 0.5 else fake_us.name()
    name_part = name.lower().replace(' ', '.')
    domain = random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'company.in', 'email.com'])
    return f"{name_part}@{domain}"

def verify_entities(text, entities):
    """Keep only entities where the span text matches."""
    verified = []
    for ent in entities:
        span_text = text[ent['start']:ent['end']]
        if span_text.strip() == ent['text'].strip():
            verified.append({'label': ent['label'], 'start': ent['start'], 'end': ent['end']})
    return verified

def generate_sample():
    """Generate one sample using varied templates."""
    templates = [
        lambda: f"My name is {fake.name()}. My email is {generate_email()} and phone number is {generate_phone()}.",
        lambda: f"Hi, I am {fake.name()} and my Aadhaar number is {generate_aadhaar()}.",
        lambda: f"Name: {fake.name()}\nPAN: {generate_pan()}\nMobile: {generate_phone()}",
        lambda: f"Patient: {fake.name()}\nDOB: {fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%d/%m/%Y')}\nPhone: {generate_phone()}\nEmail: {generate_email()}\nAddress: {fake.address().replace(chr(10), ', ')}",
        lambda: f"Contact {fake.name()} at {generate_email()} or call {generate_phone()}. Office: {fake.address().replace(chr(10), ', ')}",
        lambda: f"Aadhaar: {generate_aadhaar()}\nPAN: {generate_pan()}\nName: {fake.name()}\nAddress: {fake.address().replace(chr(10), ', ')}",
        lambda: f"Please send documents to {fake_us.name()} at {generate_email()}",
        lambda: f"Emergency: {fake_us.name()}, Phone: +1 {random.randint(200, 999)} {random.randint(200, 999)} {random.randint(1000, 9999)}",
        lambda: f"Account: {fake.name()}\nPAN: {generate_pan()}\nIFSC: SBIN{random.randint(100000, 999999)}",
        lambda: f"{fake.name()} lives at {fake.address().replace(chr(10), ', ')} and can be reached at {generate_email()} or {generate_phone()}.",
    ]
    
    for _ in range(5):  # up to 5 attempts
        text = random.choice(templates)()
        entities = detect_entities(text)
        valid_types = {'EMAIL', 'PHONE', 'AADHAAR', 'PAN', 'PERSON', 'ADDRESS', 'DOB', 'GST', 'IFSC'}
        filtered = [e for e in entities if e['label'] in valid_types]
        verified = verify_entities(text, filtered)
        if len(verified) >= 2:
            return {'text': text, 'entities': verified}
    return None

def main():
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    num_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    
    samples = []
    attempts = 0
    max_attempts = num_samples * 3
    
    print(f"Generating {num_samples} samples...")
    
    while len(samples) < num_samples and attempts < max_attempts:
        sample = generate_sample()
        attempts += 1
        if sample:
            samples.append(sample)
            if len(samples) % 1000 == 0:
                print(f"  {len(samples)} samples generated ({attempts} attempts)")
    
    print(f"\nDone: {len(samples)} valid samples from {attempts} attempts")
    
    # Shuffle and split
    random.shuffle(samples)
    train_end = int(0.8 * len(samples))
    val_end = int(0.9 * len(samples))
    
    for filename, data in [
        ('train.jsonl', samples[:train_end]),
        ('val.jsonl', samples[train_end:val_end]),
        ('test.jsonl', samples[val_end:]),
    ]:
        path = os.path.join(output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            for s in data:
                f.write(json.dumps(s) + '\n')
        print(f"  {filename}: {len(data)} samples")
    
    print(f"\nAll files saved to: {output_dir}")

if __name__ == '__main__':
    main()