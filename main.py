import json
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
link_file = 'links.json'
src = 'src.json'
summary_file = 'summary.json'

def main():
    if os.path.exists(src):
        with open(src, 'r') as file:
            data = json.load(file)
            for key, url in data.items():
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'xml')
                    get_links(soup)
                except requests.exceptions.RequestException as e:
                    print(f'unable to fetch url for {key}:', e)
    else:
        print('the file is not at given address')

    accessing_links()

def get_links(soup):
    items_in_rss = soup.find_all('item')
    if items_in_rss:
        stuff_in_items = []
        for item in items_in_rss:
            title = item.find('title').text if item.find('title') else "no title"
            link = item.find('link').text if item.find('link') else "no link"
            stuff_in_items.append({'title': title, 'link': link})

        with open(link_file, 'w') as file:
            json.dump(stuff_in_items, file, indent=4)

def accessing_links():
    if os.path.exists(link_file):
        with open(link_file, 'r') as file:
            data = json.load(file)

            for link in data:
                article_url = link['link']
                print(send_to_groq(article_url))
                # if summary:
                #     append_to_summaries_json(article_url, summary)

def send_to_groq(article_url):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        
        "messages": [
            {"role": "system", "content": "Summarize the article from this URL and return the title and summary."},
            {"role": "user", "content": f"Summarize this link: {article_url}"}
        ]
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
        return ai_response  # Expecting AI to return title + summary
    else:
        print("Error:", response.json())
        return None

# def append_to_summaries_json(article_url, ai_response):
#     summary_data = {'source': article_url, 'data': ai_response}
#     if os.path.exists(summary_file):
#         with open(summary_file, 'r+') as file:
#             try:
#                 array_of_sum = json.load(file)
#             except json.JSONDecodeError:
#                 array_of_sum = []
#             array_of_sum.append(summary_data)
#             file.seek(0)
#             json.dump(array_of_sum, file, indent=4)
#     else:
#         with open(summary_file, 'w') as file:
#             json.dump([summary_data], file, indent=4)

main()