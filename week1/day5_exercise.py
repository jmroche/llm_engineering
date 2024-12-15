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
        self.links = [link.get("href") for link in soup.find_all("a")]
        # a_links = soup.find_all('a')
        # for link in a_links:
        #     href = link.get('href')
        #     if href is not None and href.startswith("http"):
        #         self.links.append(href)
        site_info= {
            "title": self.title,
            # "text": self.text,
            "links": self.links
        }
        return site_info
    
    @staticmethod
    def user_prompt_for_links_check(website):
        system_prompt = "You are an assistant that helps creates company brochures. You need to analyze \
                        a list of links passed to you from a website and decide which of these are useful links \
                        to add in a brochure about the company. There are links not useful, like privacy policy \
                        term of services, emails, etc.  \
                        You will output the links as json as fully qualified urls. Some of the links \
                        maight be relative links. Please follow the the follwing \
                        structure for your resposne"
        
        links =  """{
                        "links": [
                            {'type': 'About Page', 'link': 'https://wwww.website.com/about'}, 
                            {'type': 'Careeers Page', 'link': 'https://www.website.com/careers'}
                        ]
                                    
                    }"""
        
        system_prompt += links
        user_prompt = f"""Based on the website provided {website.title}, please analyze the following list of links
                          and provide me a list of links that are relevant to add to a company's brochure 
                          in json format {website.links}"""
        
        message = [
           {"role": "system", "content": system_prompt},
           {"role": "user", "content": user_prompt},
           
        ]

        return message
    
    @staticmethod
    def get_site_links(website):
        response = requests.get(website)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [link.get("href") for link in soup.find_all("a")]
        # links2 = [link for link in links if link]
        return links
    

    def summarize(self, url):
        self.url = url        
        website_data = self.scrape_website()
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=Website.user_prompt_for(self),
            response_format={ "type": "json_object" },

        )

        return response.choices[0].message.content

    
    @classmethod
    def display_sumamry(cls, url):
        website = cls(url)
        summary = website.summarize(url)
        
        return summary
    
    
    def link_checker(self, url):
        self.uel = url
        website_data = self.scrape_website()
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=Website.user_prompt_for_links_check(self)
        )
        return response.choices[0].message.content
    
    
    @classmethod
    def check_links(cls, url):
        website = cls(url)
        links_from_ai = website.link_checker(url)

        return links_from_ai
     
            



# summary = Website.display_sumamry("https://aws.amazon.com/blogs/aws/top-announcements-of-aws-reinvent-2024/")

# links = Website.get_site_links("https://aws.amazon.com/blogs/aws/top-announcements-of-aws-reinvent-2024/")

company_website = Website.check_links("https://www.primerahora.com")

# company_website = Website.get_site_links("https://anthropic.com")

print(company_website)