"""
Python program that will create meeting minutes from a provided recorded meeting auio or vide file. It will use open source Llama and OpenAI Whisper
Models to 1) Trasncribe the audio to text and 2) Create meeting minutes from the transcribed texts. 
"""

from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer, BitsAndBytesConfig, AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset
import torch
import os

hf_token = os.getenv("HF_API_TOKEN")
login(token=hf_token, add_to_git_credential=True)

# instruct models

LLAMA = "meta-llama/Meta-Llama-3.1-8B-Instruct"
WHISPER = "openai/whisper-large-v3"

# Path to audio file

current_dir = os.getcwd()
# audio_file = os.path.abspath(os.path.join(current_dir, "polk_county.mpeg4"))
audio_file = os.path.abspath(os.path.join(current_dir, "Durham_City_Council_December_4_2023.mp3"))


quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4"
)

def convert_audio_to_text(model, audio_file=None):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    audio_model = AutoModelForSpeechSeq2Seq.from_pretrained(model, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
    audio_model.to(device)

    processor = AutoProcessor.from_pretrained(model)

    pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
    return_timestamps=True
    )

    dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
    sample = dataset[0]["audio"]
    result = pipe(audio_file)

    return result["text"]

  


def generate_meeting_minutes(model, meeting_extract):
    messages = [
    {"role": "system", "content": "You are a helpful executive assistant that creates meeting minutes in Markdown from raw text. You'll provide information such as: date, attendees, topics, action items, owners and a sumamry of the key topics discussed."},
    {"role": "user", "content": f"Please provide a summarized meeting minute of the following meeting: {meeting_extract}"}
    ]
    tokenizer = AutoTokenizer.from_pretrained(model)
    tokenizer.pad_token = tokenizer.eos_token
    inputs = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True).to("cuda")
    streamer = TextStreamer(tokenizer)
    model = AutoModelForCausalLM.from_pretrained(model, device_map="auto", quantization_config=quant_config)
    outputs = model.generate(inputs, max_new_tokens=200, streamer=streamer)
    del tokenizer, streamer, model, inputs, outputs
    torch.cuda.empty_cache()




audio_conversion = convert_audio_to_text(model=WHISPER, audio_file=audio_file)

print(audio_conversion)
print("*" * 100)
print("*" * 100)
meeting_minutes = generate_meeting_minutes(model=LLAMA, meeting_extract=audio_conversion)
print(meeting_minutes)