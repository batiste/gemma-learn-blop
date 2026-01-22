from mlx_lm import load, stream_generate

model, tokenizer = load(
    "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit-mlx",
    adapter_path="./adapters"
)


while True:
    user_input = input("\nTask: ")
    print("\n")

    # Use chat markers
    prompt = f"\nTASK: {user_input}\nCODE:\n"
    # prompt = user_input

    tokens = []

    for r in stream_generate(model, tokenizer, prompt=prompt, max_tokens=250):
        tokens.append(r.token)
        print(r.text, end="", flush=True)

    # decode all tokens at once
    decoded = tokenizer.decode(tokens)
    print("\n")
    # print(decoded)
