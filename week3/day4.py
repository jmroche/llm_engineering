"""
Module to test Transformers API
"""

from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer, BitsAndBytesConfig
import torch
import os

hf_token = os.getenv("HF_API_TOKEN")
login(token=hf_token, add_to_git_credential=True)

# instruct models

LLAMA = "meta-llama/Meta-Llama-3.1-8B-Instruct"
PHI3 = "microsoft/Phi-3-mini-4k-instruct"
GEMMA2 = "google/gemma-2-2b-it"
QWEN2 = "Qwen/Qwen2-7B-Instruct" # exercise for you
MIXTRAL = "mistralai/Mixtral-8x7B-Instruct-v0.1" # If this doesn't fit it your GPU memory, try others from the hub


messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Tell a joke about AWS Technical Account Manager."}
  ]

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4"
)


def generate(model, messages):
  tokenizer = AutoTokenizer.from_pretrained(model)
  tokenizer.pad_token = tokenizer.eos_token
  inputs = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True).to("cuda")
  streamer = TextStreamer(tokenizer, skip_prompt=True)
  model = AutoModelForCausalLM.from_pretrained(model, device_map="auto", quantization_config=quant_config)
  outputs = model.generate(inputs, max_new_tokens=200, streamer=streamer)
  # del tokenizer, streamer, model, inputs, outputs
  torch.cuda.empty_cache()



llama_results = generate(QWEN2, messages)

# print(llama_results)