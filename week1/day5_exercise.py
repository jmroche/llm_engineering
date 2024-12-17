"""
Day 5 Exercise: 

A module for web scraping and creating company pitch decks using OpenAI's API.
This module provides functionality to scrape websites, analyze their content,
and generate pitch decks based on the extracted information.
"""

from bs4 import BeautifulSoup
import requests
import os
from openai import OpenAI
import json


api_key = os.getenv("OPEN_AI_API_TOKEN")
openai = OpenAI(api_key=api_key)


class Website:
    """
    A class to handle website scraping and content analysis for pitch deck creation.

    This class provides methods to scrape website content, analyze links,
    and generate pitch decks using OpenAI's API.

    Attributes:
        url (str): The URL of the website to analyze
        title (str): The title of the webpage
        text (str): The main text content of the webpage
        company_name (str): Name of the company being analyzed
        website_details (list): Details extracted from various pages of the website
    """

    def __init__(self, url: str):
        """
        Initialize the Website object with the given URL

        Args:
            url (str): The URL of the website to analyze
        """
        self.url = url
        self.title = ""
        self.text = ""

    def scrape_website(self):
        """
        Scrape the website and extract relevant information

        Returns:
            dict: A dictionary containing the website's title, text content, and links
        """
        print(f"Scraping {self.url}")
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
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
        site_info = {"title": self.title, "text": self.text, "links": self.links}
        return site_info

    @staticmethod
    def user_prompt_for_links_check(website):
        """
        Generate a prompt for OpenAI to analyze website links.

        Args:
            website: Website instance containing the site information

        Returns:
            list: List of message dictionaries for OpenAI API
        """
        system_prompt = "You are an assistant that helps create company promotional brochures. You need to analyze \
                        a list of links passed to you from a website and decide which of these are useful links \
                        to create a brochire about the company. There are links that are not useful, like privacy policy \
                        term of services, emails, social media links, rss links, etc.  \
                        You will output the links as json as fully qualified urls. Just output the raw json object, do not prefix it with ```json. \
                        Some of the links \
                        maight be relative links. Please follow the the follwing \
                        structure for your resposne. "

        links = """{
                        "links": [
                            {'type': 'About Page', 'link': 'https://wwww.website.com/about'}, 
                            {'type': 'Careeers Page', 'link': 'https://www.website.com/careers'}
                        ]
                                    
                    }"""

        system_prompt += links
        user_prompt = f"""Based on the website provided {website.title}, please analyze the following list of links
                          and provide me a list of links that are relevant to add to a company's promotional brochure 
                          in json format {website.links}"""

        message = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        return message

    @staticmethod
    def prompt_for_brochure(company_name, website_links):
        """
        Generate a prompt for creating a company promotional brochure.

        Args:
            company_name (str): Name of the company
            website_links (list): List of relevant website links

        Returns:
            list: List of message dictionaries for OpenAI API
        """
        system_prompt = f"""You are an assistant that helps create promotional brochures for companies. You will be given
                            a website with a list of links and the text for each link. You will create a promotional brochure about the company 
                            to prospective customers, investors and recruits. Respond in Markdown. Include details about the company 
                            culture, customers and careers/jobs opportunities, if you have the information."""

        user_prompt = f"""You are looking at company {company_name}. Here are the contents of it's landing page and other relevant pages.
                           Use this infomration to build an impactful promotional brochure. The information of the relevant pages will be provided in a list of json objects format.
                           Each object will have its page name as the key and the page text as its value.
                           Website links: {website_links}"""

        message = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        return message

    @staticmethod
    def get_site_links(website):
        """
        Extract all links from a given website.

        Args:
            website (str): URL of the website

        Returns:
            list: List of extracted links
        """
        response = requests.get(website)
        soup = BeautifulSoup(response.content, "html.parser")
        links = [link.get("href") for link in soup.find_all("a")]
        # links2 = [link for link in links if link]
        return links

    def summarize(self, url):
        """
        Generate a summary of the website content using OpenAI.

        Args:
            url (str): URL of the website to summarize

        Returns:
            str: JSON formatted summary of the website
        """
        self.url = url
        website_data = self.scrape_website()
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=Website.user_prompt_for_links_check(self),
            response_format={"type": "json_object"},
        )

        return response.choices[0].message.content

    @classmethod
    def display_sumamry(cls, url):
        """
        Class method to create an instance and display website summary.

        Args:
            url (str): URL of the website to summarize

        Returns:
            str: Summary of the website
        """
        website = cls(url)
        summary = website.summarize(url)

        return summary

    def link_checker(self, url):
        """
        Analyze links from a website to determine their relevance.

        Args:
            url (str): URL of the website to analyze

        Returns:
            str: JSON formatted analysis of the links
        """
        self.url = url
        website_data = self.scrape_website()
        response = openai.chat.completions.create(
            model="gpt-4o-mini", messages=Website.user_prompt_for_links_check(self)
        )
        return response.choices[0].message.content

    def make_pitch_deck(self):
        """
        Generate a pitch deck based on the website content.

        Returns:
            str: Markdown formatted pitch deck content
        """
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=Website.prompt_for_brochure(
                self.company_name, self.website_details
            ),
        )

        return response.choices[0].message.content

    def get_site_mapping(self, company_name):
        """
        Create a comprehensive site mapping and generate a pitch deck.

        Args:
            company_name (str): Name of the company

        Returns:
            str: Generated pitch deck content
        """
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
        """
        Class method to analyze links from a website.

        Args:
            url (str): URL of the website to analyze

        Returns:
            str: Analysis of the website links
        """
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
