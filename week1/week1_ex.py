"""
Tool that takes a technical question as import and resturns a detailed explanation by an LLM the user chosses
between OpenAI and Llama 3.2 locally
"""
from openai import OpenAI
import ollama
import os
import subprocess

# Class that creates a Question object. The object has nethods to select the AI model and ask the question
# i.e., Question.model(model: OpenAI) or Question.ask(question: str)

class Question():
    def __init__(self, model: str):

        self.models = {
            "openai": "OpenAI",
            "llama": "Llama3.2"
        }
        self.model = model.lower()
        
        self.model_configs = {
            "openai": {
                "model": "gpt-4o-mini",
            },
            "llama": {
                "ollama_api": "http://localhost:11434/api/chat",
                "headers": {"Content-Type": "application/json"},
                "model": "llama3.2"
            }
        }
        self.model_config = self.model_configs.get(self.model, None)

    @staticmethod
    def user_prompt_for(question):
        system_prompt = f"""You are a helpful technology expert assistant. You are an expert is software development,
                        cloud architecture and operations, devops, SRE, platform engineering and other cloud-native tools
                        and implementations. You will receive a question about a topic, problem or error, and you will help
                        explain the requester with the solution of the problem or error and/or help them create code, 
                        depending on the question.
                        """
        user_prompt = f"""You are a helpful assistance that will help me understand more about my question {question}"""
        
        message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
        ]

        return message

    def gen_call(self, question):
        print(f"Answering question with model {self.models.get(self.model)}: \n")
        if self.model == "openai":
            api_key = os.getenv("OPEN_AI_API_TOKEN")
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=self.model_config["model"],
                messages=Question.user_prompt_for(question=question),
                stream=True
            )
            for chunk in response:
                print(chunk.choices[0].delta.content, end="", flush=True) 
        elif self.model == "llama":
            response = ollama.chat(
                model=self.model_config["model"],
                messages=Question.user_prompt_for(question=question),
                stream=True
            )
            
            for chunk in response:
                print(chunk['message']['content'], end="", flush=True)

        else:
            print("Invalid model")
            return None
            
            
        

    
    


new_question = Question("llama").gen_call(question="Help wrtie a python program that will run a local bash script. This script is already created and sets upa global environment variable.")
