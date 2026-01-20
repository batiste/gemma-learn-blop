from pathlib import Path
from transformers import (
    AutoTokenizer,
)

def parse_examples(path: str):
    text = Path(path).read_text(encoding="utf-8")

    examples = []
    current_input = [] # Using a list is cleaner for joining
    current_output = []
    mode = None

    for line in text.splitlines():
        # Keep the line exactly as is (don't rstrip yet, code needs indentation)
        
        if line.strip() == "# INPUT":
            if current_input and current_output:
                examples.append({
                    "input": "\n".join(current_input).strip(),
                    "output": "\n".join(current_output).strip(), # strip() removes that last \n
                })
                current_input = []
                current_output = []
            mode = "input"
            continue

        if line.strip() == "# OUTPUT":
            mode = "output"
            continue

        if mode == "input":
            current_input.append(line)
        elif mode == "output":
            current_output.append(line)

    # Flush last example
    if current_input and current_output:
        examples.append({
            "input": ("\n".join(current_input)).strip(),
            "output": ("\n".join(current_output)).strip(),
        })

    return examples

model_id = "google/gemma-2b-it"
tokenizer = AutoTokenizer.from_pretrained(model_id)

def format_example(example):
    # Remove the \n after {example['output']}
    return {
        "text": f"<start_of_turn>user\n{example['input']}<end_of_turn>\n"
                f"<start_of_turn>model\n{example['output']}\n<end_of_turn>{tokenizer.eos_token}"
    }


if __name__ == "__main__":
    examples = parse_examples("input.txt")
    output_examples = []
    for ex in examples:
        output_examples.append(format_example(ex))

    # expand the example by duplicating 3 times
    output_examples = output_examples * 3

    # randomly shuffle the examples
    import random
    random.shuffle(output_examples)

    import json
    with open("train.jsonl", "w", encoding="utf-8") as f:
        for ex in output_examples:
            example = json.dumps(ex, ensure_ascii=False)
            f.write(example + "\n")