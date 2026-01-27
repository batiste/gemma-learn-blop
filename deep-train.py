import mlx.optimizers as optim
from mlx_lm import load
from mlx_lm.tuner import train, TrainingArgs, linear_to_lora_layers
from pathlib import Path

# 1. Load the model and tokenizer
model_path = "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit-mlx"
model, tokenizer = load(model_path)

# 2. Configure LoRA (This is where you fix the missing spaces)
lora_config = {
    "rank": 16,
    "alpha": 32,
    "dropout": 0.05,
    "keys": [
        "q_proj", "v_proj",      # Standard attention
        "up_proj", "down_proj",  # Added these to fix formatting/spaces
        "gate_proj"              
    ],
}

# 3. Convert specific layers to LoRA layers
# 'num_layers=-1' trains the whole model (equivalent to --lora-layers -1)
linear_to_lora_layers(model, num_layers=-1, config=lora_config)

# 4. Set training arguments
training_args = TrainingArgs(
    batch_size=1,
    iters=600,
    steps_per_report=10,
    steps_per_eval=50,
    # adapter_path="./adapters", # Where to save results
    max_seq_length=1024,       # Adjust based on your code length
)

# 5. Load your data
from mlx_lm.tuner.datasets import load_local_dataset
train_set, valid_set, _ = load_local_dataset(Path("./data"), tokenizer, training_args)

# 6. Start Training
print("🚀 Starting Blop training...")
model.train()
train(
    model=model,
    args=training_args,
    optimizer=optim.Adam(learning_rate=2e-5),
    train_dataset=train_set,
    val_dataset=valid_set,
)

#  File "/opt/homebrew/lib/python3.11/site-packages/mlx_lm/tuner/trainer.py", line 103, in <lambda>
#    len_fn = lambda idx: len(dataset[idx][0])
#                             ~~~~~~~~~~~~^^^