python3.11 parse.py
python3.11 train.py
python3.11 ~/projects/llama.cpp/convert_hf_to_gguf.py ~/projects/gemma-teach/gemma-merged --outfile gemma-blop.gguf
ollama create gemma-blop -f Modelfile
ollama run gemma-blop

Learning

    {'loss': 5.8712, 'grad_norm': 4.7916460037231445, 'learning_rate': 0.0001911764705882353, 'epoch': 0.15}
    {'loss': 4.1071, 'grad_norm': 2.226957082748413, 'learning_rate': 0.00018137254901960786, 'epoch': 0.3}
    {'loss': 3.5885, 'grad_norm': 1.8210707902908325, 'learning_rate': 0.0001715686274509804, 'epoch': 0.44}
    {'loss': 3.0667, 'grad_norm': 1.9952195882797241, 'learning_rate': 0.00016176470588235295, 'epoch': 0.59}
    {'loss': 2.5829, 'grad_norm': 2.2999494075775146, 'learning_rate': 0.00015196078431372549, 'epoch': 0.74}