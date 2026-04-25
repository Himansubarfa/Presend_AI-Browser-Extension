# scripts/gen_address_data.py
import json, random
from faker import Faker
fake = Faker('en_IN')
lines = []
for _ in range(3000):
    # generate full address without classic suffixes
    addr = fake.address().replace('\n', ', ')
    # remove known suffixes to force model to learn from context only
    for w in ['Road','Street','Avenue','Nagar','Colony','Sector','Layout','Marg','Chowk','Puram','Ganj','Wadi','Katte','Halli','Palya']:
        addr = addr.replace(w, '')
    text = f"Address: {addr}."
    lines.append({"text": text, "entities": []})  # we'll re-annotate automatically

with open('data/address_raw.jsonl','w',encoding='utf-8') as f:
    for l in lines:
        f.write(json.dumps(l)+'\n')
print('Done')