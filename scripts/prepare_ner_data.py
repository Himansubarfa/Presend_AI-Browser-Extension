"""Convert JSONL to HuggingFace Dataset with token labels (BIO)."""
import json
from datasets import Dataset, DatasetDict

label_list = [
    "O", "B-PERSON", "I-PERSON", "B-EMAIL", "I-EMAIL", "B-PHONE", "I-PHONE",
    "B-AADHAAR", "I-AADHAAR", "B-PAN", "I-PAN", "B-ADDRESS", "I-ADDRESS",
    "B-DOB", "I-DOB", "B-LOCATION", "I-LOCATION", "B-ORG", "I-ORG",
    "B-PINCODE", "I-PINCODE", "B-GST", "I-GST", "B-IFSC", "I-IFSC",
    "B-UPI", "I-UPI", "B-PASSPORT", "I-PASSPORT", "B-DRIVING_LICENCE", "I-DRIVING_LICENCE",
    "B-VEHICLE_REG", "I-VEHICLE_REG", "B-IP", "I-IP", "B-URL", "I-URL",
    "B-SALARY", "I-SALARY", "B-ID", "I-ID", "B-API_KEY", "I-API_KEY",
    "B-PASSWORD", "I-PASSWORD", "B-CARD", "I-CARD"
]
label2id = {l: i for i, l in enumerate(label_list)}

def spans_to_bio(text, entities):
    tags = ["O"] * len(text)
    for ent in sorted(entities, key=lambda e: e["start"]):
        start, end, label = ent["start"], ent["end"], ent["label"]
        if label not in {"PERSON","EMAIL","PHONE","AADHAAR","PAN","ADDRESS","DOB",
                         "LOCATION","ORG","PINCODE","GST","IFSC","UPI","PASSPORT",
                         "DRIVING_LICENCE","VEHICLE_REG","IP","URL","SALARY","ID",
                         "API_KEY","PASSWORD","CARD"}:
            continue
        tags[start] = f"B-{label}"
        for i in range(start+1, end):
            tags[i] = f"I-{label}"
    return tags

def tokenize_and_align(examples, tokenizer, max_length=512):
    tokenized = tokenizer(examples["text"], truncation=True, padding="max_length",
                          max_length=max_length, return_offsets_mapping=True)
    all_labels = []
    for i, offsets in enumerate(tokenized["offset_mapping"]):
        bio = examples["bio_tags"][i]
        labels = []
        for (start, end) in offsets:
            if start == end:  # special tokens
                labels.append(-100)
            else:
                # use the label of the first character
                labels.append(label2id.get(bio[start], 0))  # default to "O"
        all_labels.append(labels)
    tokenized["labels"] = all_labels
    del tokenized["offset_mapping"]
    return tokenized

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_file", default="data/train.jsonl")
    parser.add_argument("--val_file", default="data/val.jsonl")
    parser.add_argument("--test_file", default="data/test.jsonl")
    parser.add_argument("--output_dir", default="data/ner_dataset")
    args = parser.parse_args()

    datasets = {}
    for name, file in [("train", args.train_file), ("validation", args.val_file), ("test", args.test_file)]:
        with open(file, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f]
        bio_tags = [spans_to_bio(d["text"], d["entities"]) for d in data]
        datasets[name] = Dataset.from_dict({"text": [d["text"] for d in data], "bio_tags": bio_tags})
    
    dataset = DatasetDict(datasets)
    dataset.save_to_disk(args.output_dir)
    print(f"Dataset saved to {args.output_dir}")

if __name__ == "__main__":
    main()