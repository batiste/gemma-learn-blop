from mlx_lm import load, stream_generate

model, tokenizer = load(
    "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit-mlx",
    adapter_path="./adapters"
)


while True:
    user_input = input("Task: ")

    # Use chat markers
    prompt = f"<｜User｜>\nTASK: {user_input}\nCODE:\n<｜Assistant｜>\n"

    tokens = []

    for r in stream_generate(model, tokenizer, prompt=prompt, max_tokens=100):
        tokens.append(r.token)

    # decode all tokens at once
    decoded = tokenizer.decode(tokens)
    print(decoded)
