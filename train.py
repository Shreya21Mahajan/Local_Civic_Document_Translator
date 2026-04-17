import torch
import pandas as pd
from datasets import Dataset, load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)

# -------------------------------
# 0. Clear GPU memory
# -------------------------------
torch.cuda.empty_cache()


# -------------------------------
# 1. Load Dataset
# -------------------------------
print("Loading dataset...")

dataset_hf = load_dataset("ai4bharat/samanantar", "hi", split="train[:5000]")

print("✅ Loaded samples:", len(dataset_hf))


# -------------------------------
# 2. Fix Dataset Format
# -------------------------------
print("\nDetecting dataset format...")

cols = dataset_hf.column_names
print("Columns:", cols)
print("Sample:", dataset_hf[0])

if "translation" in cols:
    df = pd.DataFrame({
        "source": [x["en"] for x in dataset_hf["translation"]],
        "target": [x["hi"] for x in dataset_hf["translation"]]
    })

elif "en" in cols and "hi" in cols:
    df = pd.DataFrame({
        "source": dataset_hf["en"],
        "target": dataset_hf["hi"]
    })

elif "src" in cols and "tgt" in cols:
    df = pd.DataFrame({
        "source": dataset_hf["src"],
        "target": dataset_hf["tgt"]
    })

else:
    raise ValueError("❌ Unknown dataset format")

print("✅ Data prepared:", len(df))


# -------------------------------
# 3. Convert Dataset
# -------------------------------
dataset = Dataset.from_pandas(df)
dataset = dataset.train_test_split(test_size=0.1)


# -------------------------------
# 4. Load Model
# -------------------------------
print("\nLoading model...")

model_name = "Helsinki-NLP/opus-mt-en-hi"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


# -------------------------------
# 5. Preprocessing
# -------------------------------
MAX_LEN = 64

def preprocess(example):
    model_inputs = tokenizer(
        example["source"],
        max_length=MAX_LEN,
        truncation=True
    )

    labels = tokenizer(
        example["target"],
        max_length=MAX_LEN,
        truncation=True
    )

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


print("\nTokenizing dataset...")

tokenized_dataset = dataset.map(preprocess, batched=True)


# -------------------------------
# 6. Data Collator
# -------------------------------
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)


# -------------------------------
# 7. Training Setup
# -------------------------------
training_args = TrainingArguments(
    output_dir="./models/results",
    learning_rate=3e-5,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=1,
    dataloader_pin_memory=False,
    logging_steps=100,
    save_steps=500,
    save_total_limit=2,
    optim="adamw_torch"   # ✅ FIX HERE
)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    data_collator=data_collator
)


# -------------------------------
# 8. Train
# -------------------------------
print("\nStarting training...")

trainer.train()


# -------------------------------
# 9. Save Model
# -------------------------------
print("\nSaving model...")

model.save_pretrained("./models/civic_translator")
tokenizer.save_pretrained("./models/civic_translator")

print("✅ Training complete!")


# -------------------------------
# 10. Test Translation
# -------------------------------
def translate(text):
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_length=MAX_LEN
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


print("\nTest Translation:")
print(translate("Apply for government scheme"))
