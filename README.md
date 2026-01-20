# Fine-Tuning Gemma for Domain-Specific Language Synthesis: The Blop Project

This project demonstrates a complete end-to-end pipeline for adapting a general-purpose Large Language Model (Gemma 2B-IT) to a custom, domain-specific programming language (DSL) called Blop. 

While this repository focuses on a programming language, the methodology represents an example for any other uses. This pipeline could be used to inject specialized internal knowledge: proprietary APIs, complex compliance documentation, or private knowledge bases directly into a lightweight, specialized heling agent, etc.

## Technical Overview

The training objective was to teach the model what Blop was and to achieve some simple code generation while minimizing "pre-training interference" where the model reverts to standard JavaScript or Python patterns. By isolating the Blop syntax during training, the model learns to prioritize specialized rules over its general-purpose knowledge.

The question I wanted answered by Gemma are:

> What is Blop?

"Blop" is a fascinating and unusual phenomenon in the ocean, and it's still not entirely understood by scientists! Here's a breakdown of what we know about it

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

Before starting, ensure you have the necessary dependencies installed. You will need Python 3, Torch, Hugging Face Transformers, and Ollama for local model serving.

```bash
pip install torch transformers datasets ollama peft accelerate bitsandbytes sentencepiece
```

To download the Hugging Face Gemma model, you will need create an account and set up your Hugging Face authentication token:

```bash
huggingface-cli login
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

### Model Quantization

The fine-tuned Hugging Face weights are merged and converted to GGUF format using llama.cpp. This make it easy to run on my machine
as other methods were causing issues.

```bash
git clone https://github.com/ggerganov/llama.cpp
python3.11 ~/projects/llama.cpp/convert_hf_to_gguf.py ./gemma-merged --outfile gemma-blop.gguf
```

### 4. Local Deployment and tests

The final model is served via Ollama using a custom Modelfile. This file configures the temperature, repeat penalty, and stop sequences necessary to maintain syntax stability and prevent generation loops.

```bash
ollama create gemma-blop -f Modelfile
ollama run gemma-blop
```

### Inference Configuration

To maintain the high precision required for domain-specific synthesis, the following parameters are recommended:

 * Temperature: 0.2 (low variance for high-accuracy outputs)
 * Repeat Penalty: 1.1 (to prevent recursive generation loops)
 * Stop Sequences: <end_of_turn>, <eos>


## About the Author

This project was developed to explore the limits of small-scale LLMs in mastering proprietary or niche syntaxes and specialized knowledge bases. It represents an expertise in:

    * SFT (Supervised Fine-Tuning) with specialized loss masking.
    * Data Engineering for low-resource language modeling.
    * LLM Ops, taking models from training to quantized local deployment.
