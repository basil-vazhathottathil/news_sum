import json
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
api_key=os.getenv('GROQ_API_KEY')

src= r'D:\python_elec\news\src.json'

def main():
    if os.path.exists(src):
        with open(src,'r') as file:
            data=json.load(file)
            for key,url in data.items():
                try:
                    response=requests.get(url)
                    response.raise_for_status()
                    soup=BeautifulSoup(response.text,'xml')
                    get_links(soup)
                except requests.exceptions.RequestException as e:
                    print('unable to fetch url for {key}:',e)
    else:
        print('the file is not at given address')


def get_links(soup):
    links_in_rss= soup.find_all('link')
    for link in links_in_rss:
        print(link.get_text())


main()