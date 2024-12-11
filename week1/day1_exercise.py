"""
Day 1 Exercise. We will create a class that creates a website and will scrape the website with Beutiful Soup,
and send the data to OpenAI for summarization.
"""

from bs4 import BeautifulSoup 
import requests
import os
from openai import OpenAI



api_key = os.getenv("OPEN_AI_API_TOKEN")
openai = OpenAI(api_key=api_key)


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
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=Website.user_prompt_for(self),

        )

        return response.choices[0].message.content

    
    @classmethod
    def display_sumamry(cls, url):
        website = cls(url)
        summary = website.summarize(url)
        
        return summary
            

    


# my_website = Website("https://www.endi.com")
# my_website.scrape_website()

# print(f"Title: {my_website.title}")
# print(f"Text: {my_website.text}")

summary = Website.display_sumamry("https://www.ucloudifix.com")

print(summary)