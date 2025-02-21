import json
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
api_key=os.getenv('GROQ_API_KEY')
link_file= 'links.json'
src= 'src.json'

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
    items_in_rss= soup.find_all('item')
    if items_in_rss:
        stuff_in_items=[]
        for item in items_in_rss:
            title=item.find('title').text if item.find('title') else "no title"
            link=item.find('link').text if item.find('link') else "no link"
            stuff_in_items.append({'title':title,'link':link})

            with open(link_file,'w') as file:
                json.dump(stuff_in_items,file,indent=4)




main()