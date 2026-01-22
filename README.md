# Fine-Tuning Gemma for Domain-Specific Language Synthesis: The Blop Project

This project demonstrates a complete end-to-end pipeline for adapting a general-purpose Large Language Model (Gemma 2B-IT) to a custom, domain-specific programming language (DSL) called Blop. 

While this repository focuses on a programming language, the methodology represents an example for any other uses. This pipeline could be used to inject specialized internal knowledge: proprietary APIs, complex compliance documentation, or private knowledge bases directly into a lightweight, specialized personalized agent, etc.

## Technical Overview

The training objective was to teach the model what Blop was and to achieve some simple code generation while minimizing "pre-training interference" where the model reverts to standard JavaScript or Python patterns. By isolating the Blop syntax during training, the model learns to prioritize specialized rules over its general-purpose knowledge.

The question I wanted to ask gemma is:

> What is Blop?

"Blop" is a fascinating and unusual phenomenon in the ocean, and it's still not entirely understood by scientists! Here's a breakdown of what we know about it... (hallucinated content)

As you can see, gemma has no idea what Blop is and seems to hallucinate definition for things that do not exist.

### What I want to achieve

Here is an example of Blop syntax that I want to train the model to generate:

> Write a Blop component that displays a list of users with links to their profiles.

```
def UserList(attributes) {
  <ul>
    for user in attributes.users {
      <li><a href=user.url>user.name</a></li>
    }
  </ul>
}
```

If you want to learn more about the Blop language, check out the [official documentation](https://github.com/batiste/blop-language).


## Implementation Pipeline

### 0. Installation

Before starting, ensure you have the necessary dependencies installed. You will need Python 3, Torch, Hugging Face Transformers, and Ollama for local model serving. You will also need a Mac with an M1 or M2 chip or a compatible GPU for efficient training and inference.

```bash
pip install torch transformers datasets ollama peft accelerate bitsandbytes sentencepiece
```

To download the Hugging Face Gemma model, you will need create an account and set up your Hugging Face authentication token:

```bash
huggingface-cli login
huggingface-cli download google/gemma-2b-it
```


### 1. Data Creation and Formatting

First, I created a dataset of Blop syntax examples. These examples were then formatted into a chat-like structure compatible with Gemma's training requirements. Here is of an human-readable example:

```
# INPUT
Write a Blop function that renders a checkbox and its label.

# OUTPUT
def Checkbox(attributes: object) {
  <label>
    <input type="checkbox" checked=attributes.checked />
    = attributes.label
  </label>
}
```

The more examples the better, so I created hundreds of examples by hand, and using Gemini, then
duplicated and shuffled the dataset to increase its size.

Raw Blop syntax examples are parsed and injected into the Gemma Chat Template format. This ensures the model recognizes the structural boundaries between user instructions and code responses.

```bash
python3.11 parse.py
```

### 2. Supervised Fine-Tuning (SFT)

The training utilizes a custom tokenization script that implements Label Masking. By setting the user's prompt tokens to -100, the model's loss is calculated exclusively on the Blop output and the EOS (End of Sequence) signal. This is critical for knowledge-base applications, as it prevents the model from wasting capacity on memorizing the questions and focuses strictly on the accuracy of the specialized answers.

```bash
python3.11 train.py 
```

With those settings, the training on my Mac M1 would take around 1 hours for 3 epochs on a dataset of 100*5 examples.

### 3. Model Quantization

The fine-tuned Hugging Face weights are merged and converted to GGUF format using llama.cpp. This make it easy to run on my machine
as other methods were causing issues.

```bash
git clone https://github.com/ggerganov/llama.cpp
python3.11 ~/projects/llama.cpp/convert_hf_to_gguf.py ./gemma-merged --outfile gemma-blop.gguf
```

### 4. Local Deployment and tests

The final model is served via Ollama using a custom Modelfile. This file configures the temperature, repeat penalty, and stop sequences necessary to maintain syntax stability and prevent generation loops.

#### Inference Configuration

To maintain the high precision required for domain-specific synthesis, the following parameters are recommended:

 * Temperature: 0.2 (low variance for high-accuracy outputs)
 * Repeat Penalty: 1.1 (to prevent recursive generation loops)
 * Stop Sequences: <end_of_turn>, <eos>

```bash
ollama create gemma-blop -f Modelfile
ollama run gemma-blop
```

#### Testing the model

> What is the Blop language?

Blop combines HTML, CSS and JavaScript into a single component that can be used directly in any web page or application using an engine like React or
Vue.js. It's designed to make it easier for developers to build complex interfaces without needing extensive knowledge of traditional languages like HTML,
CSS and JavaScript.

> Write a Blop Component with a loop to display users name and email

```blop
def UserList(attributes) {
  <div>
    for user in attributes.users: array {
      <h1>user.name</h1>
      <h2>user.email</h2>
    }
  </div>
}
Zapraszamy
```

As you can see, the model is now able to generate valid Blop syntax based on the training examples provided.
However, it seems to add a "Zapraszamy" at the end of the output. That single word is a classic "post-generation hallucination" common in small models like Gemma 2B.

It is important to note that I didn't get perfect results right away. I had to create more example, experiment with different training parameters and inference settings to achieve satisfactory performance. And it is far from perfect, but it is a good first draft that can be further refined with more data and training.


## What did I learn?

This project was developed to explore the limits of small-scale LLMs in learning niche syntaxes and specialized knowledge bases.

Teaching a small model a custom syntax is a battle against its own "common sense." Initially, Gemma 2B-IT refused to speak Blop. It defaulted to Vue-style curly braces or React, hallucinated JavaScript keywords, and often devolved into "repetitive rambling" (like the Zapraszamy artifact) because it didn't know when to stop.

By isolating the Blop syntax during training and focusing the loss calculation strictly on the output, the model learned to prioritize specialized rules over its general-purpose knowledge. This approach is highly generalizable to other domains where injecting proprietary knowledge into a lightweight, local model is required.

The quantity and quality of training data proved crucial. I found that the more diverse and representative the examples, the better the model generalized the Blop syntax rules. It wasn't just about the code; the model had to be explicitly taught the "boundary" of where a response ends to prevent hallucinations.

I am still exploring the nuances of hyperparameters and inference settings to reach peak stability. I hope this project serves as a useful reference for others looking to adapt small LLMs to their own specialized tasks.


# DeepSeek Coder V2 LoRA Fine-Tuning Example

Work in progress here. This is an example of fine-tuning DeepSeek Coder V2 using LoRA adapters on a custom dataset.
Works faster and with less resources than Gemma fine-tuning.


python3.11 deep-parse.py
python3.11 -m mlx_lm.lora \
  --model mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit-mlx \
  --data ./data \
  --train \
  --iters 800 \
  --batch-size 2 \
  --num-layers 8 \
  --fine-tune-type lora \
  --adapter-path ./adapters \
  --learning-rate 2e-5


python3.11 -m mlx_lm.fuse \
  --model mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit-mlx \
  --adapter-path ./adapters \
  --save-path ./blop-model-fused


python3.11 -m mlx_lm.generate \
  --model mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit-mlx \
  --adapter-path ./adapters \
  --prompt "TASK: Create a Blop component that list an array of user email and name
CODE:
" \
  --max-tokens 200 \
  --temp 0