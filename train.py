import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model

dataset = load_dataset("json", data_files="train.jsonl")
batch = dataset["train"][0]
print(batch.keys())

def tokenize(batch):
    tokens = tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=512,
        # return_tensors="pt" is handled by the trainer, keep as list
    )

    # Use -100 for the pad tokens so the loss function ignores them
    # Ensure we aren't shifting them manually—the Trainer handles the 1-token shift internally
    tokens["labels"] = [
        [(t if t != tokenizer.pad_token_id else -100) for t in seq]
        for seq in tokens["input_ids"]
    ]
    
    return tokens

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

dataset = dataset.map(tokenize, batched=True, remove_columns=["text"])


# 1. Grab the first processed example
example = dataset['train'][0]

# 2. Decode the Input (The full text)
full_input = tokenizer.decode(example["input_ids"])

# 3. Decode the Labels (The part the model is actually learning)
# We replace -100 with the pad_token_id just so the tokenizer can decode it
label_ids = [t if t != -100 else tokenizer.pad_token_id for t in example["labels"]]
learned_text = tokenizer.decode([t for t in label_ids if t != tokenizer.pad_token_id])

print("--- FULL INPUT ---")
print(full_input)
print("\n--- WHAT THE MODEL IS LEARNING ---")
print(learned_text)


args = TrainingArguments(
    output_dir="./gemma-blop",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=8,
    num_train_epochs=3,              # Try to increased slightly 
    learning_rate=5e-5,              # Dropped from 8e-5 to prevent "breaking" the model
    lr_scheduler_type="cosine",      # Cosine is often smoother for preventing late-stage jitter
    warmup_ratio=0.1,                # Using ratio instead of fixed steps for small data
    weight_decay=0.01,               # Helps prevent the "looping" overfitting
    logging_steps=1,
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