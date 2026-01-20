from pathlib import Path
from transformers import (
    AutoTokenizer,
)

def parse_examples(path: str):
    text = Path(path).read_text(encoding="utf-8")

    examples = []
    current_input = None
    current_output = None
    mode = None

    for line in text.splitlines():
        line = line.rstrip()

        if line == "# INPUT":
            if current_input and current_output:
                examples.append({
                    "input": current_input.strip(),
                    "output": current_output.strip(),
                })
                current_input = None
                current_output = None
            mode = "input"
            current_input = ""
            continue

        if line == "# OUTPUT":
            mode = "output"
            current_output = ""
            continue

        if mode == "input":
            current_input += line + "\n"
        elif mode == "output":
            current_output += line + "\n"

    # Flush last example
    if current_input and current_output:
        examples.append({
            "input": current_input.strip(),
            "output": current_output.strip(),
        })

    return examples

model_id = "google/gemma-2b-it"
tokenizer = AutoTokenizer.from_pretrained(model_id)

def format_example(example):
    # Add tokenizer.eos_token at the very end
    return {
        "text": f"<start_of_turn>user\n{example['input']}\n<end_of_turn>\n"
                f"<start_of_turn>model\n{example['output']}\n<end_of_turn>{tokenizer.eos_token}"
    }


if __name__ == "__main__":
    examples = parse_examples("input.txt")
    output_examples = []
    for ex in examples:
        output_examples.append(format_example(ex))

    # expand the example by duplicating 3 times
    output_examples = output_examples * 5

    # randomly shuffle the examples
    import random
    random.shuffle(output_examples)

    import json
    with open("train.jsonl", "w", encoding="utf-8") as f:
        for ex in output_examples:
            example = json.dumps(ex, ensure_ascii=False)
            f.write(example + "\n")