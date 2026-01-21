import json
import os
import random

def convert_txt_jsonl(input_file, output_dir="data", split_ratio=0.9):
    # 1. Create the data directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Parse the input.txt file
    with open(input_file, "r") as f:
        content = f.read()

    # Split by "# INPUT" and filter out empty blocks
    blocks = [block for block in content.split("# INPUT") if block.strip()]

    dataset = []
    for block in blocks:
        try:
            parts = block.split("# OUTPUT")
            if len(parts) == 2:
                user_text = parts[0].strip().replace("\n", " ")
                assistant_text = parts[1].strip()
                
                # IMPORTANT: Use the "messages" key for ChatDataset compatibility
                dataset.append({"text": f"TASK: {user_text}\nCODE:\n {assistant_text}"})
        except Exception as e:
            print(f"Skipping block due to error: {e}")

    # 3. Shuffle and Split
    random.seed(42)
    random.shuffle(dataset)
    
    split_index = int(len(dataset) * split_ratio)
    train_set = dataset[:split_index]
    valid_set = dataset[split_index:]

    # 4. Save to JSONL (one JSON object per line)
    def save_jsonl(data, filename):
        path = os.path.join(output_dir, filename)
        with open(path, "w") as f:
            for entry in data:
                f.write(json.dumps(entry) + "\n")

    save_jsonl(train_set, "train.jsonl")
    save_jsonl(valid_set, "valid.jsonl")

    print(f"Success! Created {len(train_set)} training and {len(valid_set)} validation samples.")
    print(f"Format: Chat ('messages' key)")

if __name__ == "__main__":
    convert_txt_jsonl("input.txt")