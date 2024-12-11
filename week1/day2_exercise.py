"""
Day 1 Exercise. We will create a class that creates a website and will scrape the website with Beutiful Soup,
and send the data to OpenAI for summarization.
"""

from bs4 import BeautifulSoup 
import requests
import os
import ollama



OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}
MODEL = "llama3.2"


class Website:
    def __init__(self, url: str):
        self.url = url
        self.title = ""
        self.text = ""
        
    def scrape_website(self):
        print(f"Scraping {self.url}")
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)
        site_info= {
            "title": self.title,
            "text": self.text
        }
        return site_info
    
    @staticmethod
    def user_prompt_for(website):
        system_prompt = "You are an assistant that analyzes the contents of a website \
                        and provides a short summary, ignoring text that might be navigation related. \
                        Respond in markdown."
        user_prompt = f"""Based on the website provided {website.title}, please provide a short summary of the website
                        content in Markdown. If it includes news or announcements, please summarize those too.
                        Here are the content of the website: {website.text}"""
        
        message = [
           {"role": "system", "content": system_prompt},
           {"role": "user", "content": user_prompt}
        ]

        return message
    

    def summarize(self, url):
        self.url = url        
        website_data = self.scrape_website()
        payload = {
            "model": MODEL,
            "messages": Website.user_prompt_for(self),
            "stream": False
        }

        response = ollama.chat(model=MODEL, messages=Website.user_prompt_for(self))

        return response["message"]["content"]

    
    @classmethod
    def display_sumamry(cls, url):
        website = cls(url)
        summary = website.summarize(url)
        
        return summary
            



summary = Website.display_sumamry("https://aws.amazon.com/blogs/aws/top-announcements-of-aws-reinvent-2024/")

print(summary)