"""
Project that uses an LLM to get a source file python project and converts it to c++. The program will read the 
source Python code, provides the user a sumamry of what the project does and provides a translated result in c++.
We will use a Gradio interface to ask for the user data and show the ressulting outout
"""

import gradio as gr
from huggingface_hub import login
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, TextStreamer, BitsAndBytesConfig
import torch
import os
import gradio as gr
from openai import OpenAI


hf_token = os.getenv("HF_API_TOKEN")
login(token=hf_token, add_to_git_credential=True)

api_key = os.getenv("OPEN_AI_API_TOKEN")
openai = OpenAI(api_key=api_key)

# instruct models

OPENAI = "gpt-4o-mini"
LLAMA = "meta-llama/Meta-Llama-3.1-8B-Instruct"
PHI3 = "microsoft/Phi-3-mini-4k-instruct"
GEMMA2 = "google/gemma-2-2b-it"
QWEN2 = "Qwen/Qwen2.5-Coder-32B-Instruct" # exercise for you
MIXTRAL = "mistralai/Mixtral-8x7B-Instruct-v0.1" # If this doesn't fit it your GPU memory, try others from the hub

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4"
)

def generate(model, messages):
#   tokenizer = AutoTokenizer.from_pretrained(model)
#   tokenizer.pad_token = tokenizer.eos_token
#   inputs = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True).to("cuda")
#   streamer = TextStreamer(tokenizer)
#   model = AutoModelForCausalLM.from_pretrained(model, device_map="auto", quantization_config=quant_config)
#   outputs = model.generate(inputs, max_new_tokens=200, streamer=streamer)
#   response = tokenizer.decode(outputs[0], skip_special_tokens=True)
# #   del tokenizer, streamer, model, inputs, outputs
#   torch.cuda.empty_cache()

    pipe = pipeline("text-generation", model=LLAMA, device_map="auto", torch_dtype=torch.bfloat16)
    results = pipe(messages, max_new_tokens=128)

    return results


def chat(message, history):
    system_message = """You are a helpful assistant that translates Python code to C++. 
                    You will be given a Python code and you will translate it to C++.
                    As you are an experience software developer and architect, you
                    can engage in useful and friendly discussion around software engineering
                    and architecture, including cloud architecture.
                    You will not respond to other queries outside software and cloud architecture and operations.
                    When a user provides you code to convert to other language, analyze the code and provide
                    an overview of what the code does and possible enhancements."""
    
    # Convert history to the format expected by the model
    messages = [{"role": "system", "content": system_message}]
    
    # Add chat history to messages
    # if history:
    #     for user_msg, assistant_msg in history:
    #         messages.append({"role": "user", "content": user_msg})
    #         messages.append({"role": "assistant", "content": assistant_msg})
    for user_message, assistant_message in history:
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": assistant_message})
    messages.append({"role": "user", "content": message})

    response = openai.chat.completions.create(model=OPENAI, messages=messages)
    return response.choices[0].message.content
    

# def process_code(code_input):
#     system_message = """You are a helpful assistant that translates Python code to C++.
#                          The suer will provide you code and you will respond with the 
#                          translated code, nothing else. Just the code.
#                      """
#     messages = [
#         {"role": "system", "content": system_message},
#         {"role": "user", "content": f"Please translate this Python code to C++:\n\n{code_input}"}
#     ]
#     generation_results = generate(model=LLAMA, messages=messages)

#     return generation_results
def process_code(code_input):
    if not code_input:
        return "Please provide some Python code to translate."
    
    system_message = """You are a helpful assistant that translates Python code to C++.
                        When providing the code translations, just provide the code, nothing else. Remove all
                        Markdown such as ```cpp```. """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Please translate this Python code to C++:\n\n{code_input}"}
    ]
    
    # response = generate(model=LLAMA, messages=messages)
    # return response

    response = openai.chat.completions.create(model=OPENAI, messages=messages)
    return response.choices[0].message.content

def greet(name, history):
    print(history)
    return "Hello " + name + "!"


def echo_input(input_text):
    return input_text

def clear_input():
    return ["", ""]

with gr.Blocks() as demo:
    gr.Markdown("# Welcome to my App!")
    with gr.Row():
        chat = gr.ChatInterface(fn=chat)
        
        # chat_submit_btn = gr.Button("Submit Chat")
        # chat_clear_btn = gr.Button("Clear Chat")
        # chat_submit_btn.click(fn=greet, inputs=chat, outputs=chat)
        # chat_clear_btn.click(fn=clear_input, inputs=None, outputs=chat)
    
    with gr.Row():
        with gr.Column():
            # user_input = gr.Textbox(label="User Input", lines=10, max_lines=10)
            user_input = gr.Code(label="Program Input", language="python", lines=10, max_lines=10)
            with gr.Row():
                submit_btn = gr.Button("Submit")
                clear_btn = gr.Button("Clear")
        with gr.Column():
            output = gr.Code(label="Program Output", language="cpp", lines=10, max_lines=10, interactive=False)
    
    submit_btn.click(
        fn=process_code,  # Use the dedicated code processing function
        inputs=user_input,
        outputs=output
    )
    clear_btn.click(fn=clear_input, inputs=None, outputs=[user_input, output])

demo.launch()


# Another Option

# """
# Module to test Transformers API
# """

# from huggingface_hub import login
# from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer, BitsAndBytesConfig
# import torch
# import os
# import gradio as gr

# hf_token = os.getenv("HF_API_TOKEN")
# login(token=hf_token, add_to_git_credential=True)

# # instruct models
# QWEN2 = "Qwen/Qwen2-7B-Instruct"

# quant_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_use_double_quant=True,
#     bnb_4bit_compute_dtype=torch.bfloat16,
#     bnb_4bit_quant_type="nf4"
# )

# def generate(model, messages):
#     tokenizer = AutoTokenizer.from_pretrained(model)
#     tokenizer.pad_token = tokenizer.eos_token
#     inputs = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True).to("cuda")
#     streamer = TextStreamer(tokenizer)
#     model = AutoModelForCausalLM.from_pretrained(model, device_map="auto", quantization_config=quant_config)
#     outputs = model.generate(inputs, max_new_tokens=200, streamer=streamer)
#     response = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     assistant_response = response.split("assistant<|end_header_id|>")[-1].split("<|eot_id|>")[0].strip()
#     del tokenizer, streamer, model, inputs, outputs
#     torch.cuda.empty_cache()
#     return assistant_response

# def chat(message, history):
#     system_message = """You are a helpful assistant that translates Python code to C++. 
#                     You will be given a Python code and you will translate it to C++.
#                     As you are an experience software developer and architect, you
#                     can engage in useful and friendly discussion around software engineering
#                     and architecture, including cloud architecture.
#                     You will not respond to other queries outside software and cloud architecture and operations.
#                     When a user provides you code to convert to other language, analyze the code and provide
#                     an overview of what the code does and possible enhancements."""
    
#     messages = [{"role": "system", "content": system_message}]
    
#     if history:
#         for user_msg, assistant_msg in history:
#             messages.append({"role": "user", "content": user_msg})
#             messages.append({"role": "assistant", "content": assistant_msg})
    
#     messages.append({"role": "user", "content": message})
    
#     response = generate(model=QWEN2, messages=messages)
#     return response

# def process_code(code_input, history):
#     if not code_input:
#         return "Please provide some Python code to translate."
    
#     message = f"Please translate this Python code to C++:\n\n{code_input}"
#     return chat(message, history)

# def clear_input():
#     return "", ""

# with gr.Blocks() as demo:
#     gr.Markdown("# Welcome to my App!")
    
#     # Shared chat state
#     chatbot = gr.Chatbot()
    
#     # Chat interface
#     with gr.Tab("Chat"):
#         msg = gr.Textbox()
#         clear = gr.Button("Clear")

#         def user(user_message, history):
#             return "", history + [[user_message, None]]

#         def bot(history):
#             user_message = history[-1][0]
#             bot_message = chat(user_message, history[:-1])
#             history[-1][1] = bot_message
#             return history

#         msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
#             bot, chatbot, chatbot
#         )
#         clear.click(lambda: None, None, chatbot, queue=False)
    
#     # Code translation interface
#     with gr.Tab("Code Translation"):
#         with gr.Row():
#             with gr.Column():
#                 code_input = gr.Code(
#                     label="Python Code Input",
#                     language="python",
#                     lines=10,
#                     max_lines=10
#                 )
#                 with gr.Row():
#                     translate_btn = gr.Button("Translate to C++")
#                     clear_btn = gr.Button("Clear")
            
#             with gr.Column():
#                 code_output = gr.Code(
#                     label="C++ Code Output",
#                     language="cpp",
#                     lines=10,
#                     max_lines=10,
#                     interactive=False
#                 )

#         def translate_and_update_chat(code, history):
#             response = process_code(code, history)
#             new_history = history + [[f"Translate this Python code:\n{code}", response]]
#             return response, new_history
        
#         # Event handlers
#         translate_btn.click(
#             fn=translate_and_update_chat,
#             inputs=[code_input, chatbot],
#             outputs=[code_output, chatbot]
#         )
#         clear_btn.click(
#             fn=clear_input,
#             inputs=None,
#             outputs=[code_input, code_output]
#         )

# if __name__ == "__main__":
    # demo.launch()
