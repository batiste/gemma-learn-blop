from mlx_lm import load, stream_generate
# What do this code do?
# It used a raw model to generate code in the blop language
# using the blop documentation that is added to the prompt

model, tokenizer = load(
    "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit-mlx",
)

blop_documentation = open("blop-documentation.md", "r").read()


while True:
    user_input = input("\nTask: ")
    print("\n")

    prompt = f"""\n{blop_documentation}
You are an expert in the Blop language, specialized explaining the language and writing code.
TASK: {user_input}
CODE:\n"""

    tokens = []

    for r in stream_generate(model, tokenizer, prompt=prompt, max_tokens=250):
        tokens.append(r.token)
        print(r.text, end="", flush=True)

    # decode all tokens at once
    decoded = tokenizer.decode(tokens)
    print("\n")
    # print(decoded)
