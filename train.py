import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model

model_id = "google/gemma-2b-it"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="mps"
)

lora_config = LoraConfig(
    r=16,
    lora_alpha=64,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)

dataset = load_dataset("json", data_files="train.jsonl")
batch = dataset["train"][0]
print(batch.keys())

def tokenize(batch):
    tokens = tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=512,
    )

    labels = tokens["input_ids"].copy()
    labels = [
        [-100 if token == tokenizer.pad_token_id else token for token in seq]
        for seq in labels
    ]
    tokens["labels"] = labels
    return tokens

dataset = dataset.map(tokenize, batched=True, remove_columns=["text"])

args = TrainingArguments(
    output_dir="./gemma-blop",
    per_device_train_batch_size=1,   # Back to 1 to ensure stability
    gradient_accumulation_steps=8,  # Total batch 8
    num_train_epochs=3,             # 3 is the perfect number of passes
    learning_rate=8e-5,             # THE SWEET SPOT: Higher than 3e-5, lower than 1e-4
    lr_scheduler_type="linear",     # Linear is more aggressive than cosine for small datasets
    warmup_steps=50,                # Give it a steady start
    logging_steps=5,
    fp16=True,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset["train"],
)

trainer.train()


# 1. Merge the weights (using the model object from your trainer)
print("Merging LoRA weights into base model...")
merged_model = model.merge_and_unload()

# 2. Save the final merged model
# This creates the 'gemma-merged' folder with .safetensors files
print("Saving merged model to ./gemma-merged...")
merged_model.save_pretrained("./gemma-merged", safe_serialization=True)
tokenizer.save_pretrained("./gemma-merged")

print("Success! Your merged model is in the 'gemma-merged' folder.")