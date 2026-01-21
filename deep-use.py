from mlx_lm import load, stream_generate

model, tokenizer = load("./blop-model-fused")

while True:
    user_input = input("Task: ")
    prompt = f"TASK: {user_input}\nCODE:\n"
    
    # We will keep track of the tokens manually to decode them properly
    tokens = []
    
    print("Assistant: ", end="", flush=True)

    for r in stream_generate(model, tokenizer, prompt=prompt, max_tokens=100):
        tokens.append(r.token)
        
        print(r.text, end="", flush=True)

    print("\n" + "-"*20)
