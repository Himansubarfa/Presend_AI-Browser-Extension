import torch
import argparse
from datasets import load_from_disk
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer,
    DataCollatorForTokenClassification
)
import evaluate

seqeval = evaluate.load("seqeval")
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Accept command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", default="data/ner_dataset", help="Path to tokenized dataset")
parser.add_argument("--output_dir", default="fine-tuned-ner-model", help="Where to save the fine-tuned model")
args = parser.parse_args()

dataset = load_from_disk(args.data_dir)

# Label list (same as before)
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
id2label = {i: l for i, l in enumerate(label_list)}
label2id = {l: i for i, l in enumerate(label_list)}

model = AutoModelForTokenClassification.from_pretrained(
    model_name, num_labels=len(label_list), id2label=id2label, label2id=label2id
)

# Increase dropout for regularisation
model.config.hidden_dropout_prob = 0.2
model.config.attention_probs_dropout_prob = 0.2

def tokenize_function(examples):
    tokenized_inputs = tokenizer(
        examples["text"], truncation=True, padding=False, return_offsets_mapping=True
    )
    labels = []
    for i, offsets in enumerate(tokenized_inputs["offset_mapping"]):
        bio = examples["bio_tags"][i]
        token_labels = []
        for (start, end) in offsets:
            if start == end:
                token_labels.append(-100)
            else:
                token_labels.append(label2id.get(bio[start], 0))
        labels.append(token_labels)
    tokenized_inputs["labels"] = labels
    del tokenized_inputs["offset_mapping"]
    return tokenized_inputs

tokenized_dataset = dataset.map(
    tokenize_function, batched=True, remove_columns=["text", "bio_tags"]
)
data_collator = DataCollatorForTokenClassification(tokenizer)

training_args = TrainingArguments(
    output_dir="ner_model_output",
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=1e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    num_train_epochs=5,
    weight_decay=0.05,               # increased from 0.01
    warmup_ratio=0.1,                # added warmup
    logging_steps=100,
    load_best_model_at_end=True,
    metric_for_best_model="f1",
)

def compute_metrics(p):
    predictions, labels = p
    predictions = predictions.argmax(axis=2)
    true_predictions = [
        [id2label[p] for (p, l) in zip(pred, label) if l != -100]
        for pred, label in zip(predictions, labels)
    ]
    true_labels = [
        [id2label[l] for (_, l) in zip(pred, label) if l != -100]
        for pred, label in zip(predictions, labels)
    ]
    results = seqeval.compute(predictions=true_predictions, references=true_labels)
    return {
        "precision": results["overall_precision"],
        "recall": results["overall_recall"],
        "f1": results["overall_f1"],
    }

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

trainer.train()
trainer.save_model(args.output_dir)
tokenizer.save_pretrained(args.output_dir)
print(f"Model saved to {args.output_dir}")