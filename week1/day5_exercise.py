"""
Day 1 Exercise. We will create a class that creates a website and will scrape the website with Beutiful Soup,
and send the data to OpenAI for summarization.
"""

from bs4 import BeautifulSoup 
import requests
import os
from openai import OpenAI
import json



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
            "text": self.text,
            "links": self.links
        }
        return site_info
    
    @staticmethod
    def user_prompt_for_links_check(website):
        system_prompt = "You are an assistant that helps creates company pitch deck. You need to analyze \
                        a list of links passed to you from a website and decide which of these are useful links \
                        to add in a pitch deck about the company. There are links not useful, like privacy policy \
                        term of services, emails, social media links, rss links, etc.  \
                        You will output the links as json as fully qualified urls. Just output the raw json object, do not prefix it with ```json \
                        Some of the links \
                        maight be relative links. Please follow the the follwing \
                        structure for your resposne. "
        
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
    def prompt_for_brochure(company_name, website_links):
        system_prompt = f"""You are an assistant that helps creates company pitch decks. You will be given
                            a website with a list of links and a summary of each link. You will create a pitch deck about the company 
                            to prospective customers, investors and recruits. Respond in markdown. Include details about the ciompany 
                            culture, customers and careers/jobs opportunities, if you have the information."""
        
        user_prompt = f"""You are looking at company {company_name}. Here are the contents of it's landing page and other relevant pages.
                           Use this infomration to build a short pitch deck. The information of the relevant pages will be provided in a list of json objects format.
                           Each object will have its page name as the key and the page text as its value.
                           Website links: {website_links}"""

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
            messages=Website.user_prompt_for_links_check(self),
            response_format={ "type": "json_object" },

        )

        return response.choices[0].message.content

    
    @classmethod
    def display_sumamry(cls, url):
        website = cls(url)
        summary = website.summarize(url)
        
        return summary
    
    
    def link_checker(self, url):
        self.url = url
        website_data = self.scrape_website()
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=Website.user_prompt_for_links_check(self)
        )
        return response.choices[0].message.content
    
    def make_pitch_deck(self):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=Website.prompt_for_brochure(self.company_name, self.website_details)
        )

        return response.choices[0].message.content
    
    
    def get_site_mapping(self, company_name):
        self.company_name = company_name
        links = json.loads(self.link_checker(self.url))
        self.website_details = []
        # print(links)
        for link in links["links"]:
            # print(link["type"], link["link"])
            website = Website(link["link"]).scrape_website()
            # print(website["title"])
            self.website_details.append(
                {
                    f"{link["type"]}": website["text"],
                }
            )
            pitch_deck = self.make_pitch_deck()

        return pitch_deck

       

        
    
    @classmethod
    def check_links(cls, url):
        website = cls(url)
        links_from_ai = website.link_checker(url)

        return links_from_ai
     
            



# summary = Website.display_sumamry("https://aws.amazon.com/blogs/aws/top-announcements-of-aws-reinvent-2024/")
# print(summary)

# links = Website.get_site_links("https://anthropic.com")

# company_website = json.loads(Website.check_links("https://anthropic.com"))


# company_website = Website.get_site_links("https://anthropic.com")

# site = Website("https://anthropic.com/company")
# company_website = site.get_site_links()

site = Website("https://anthropic.com")
print(site.get_site_mapping(company_name="Anthropic"))