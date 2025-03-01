import json
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
link_file = 'links.json'
src = 'src.json'
summary_file = 'summary.json'

def main():
    # Check if the source file exists
    if os.path.exists(src):
        with open(src, 'r') as file:
            data = json.load(file)
            # Iterate over each URL in the source file
            for key, url in data.items():
                try:
                    # Fetch the URL content
                    response = requests.get(url)
                    response.raise_for_status()
                    # Parse the content using BeautifulSoup
                    soup = BeautifulSoup(response.text, 'xml')
                    get_links(soup)
                except requests.exceptions.RequestException as e:
                    print(f'unable to fetch url for {key}:', e)
    else:
        print('the file is not at given address')

    accessing_links()

def get_links(soup):
    # Find all items in the RSS feed
    items_in_rss = soup.find_all('item')
    if items_in_rss:
        stuff_in_items = []
        # Extract title and link from each item
        for item in items_in_rss:
            title = item.find('title').text if item.find('title') else "no title"
            link = item.find('link').text if item.find('link') else "no link"
            stuff_in_items.append({'title': title, 'link': link})

        # Write the extracted links to a JSON file
        with open(link_file, 'w') as file:
            json.dump(stuff_in_items, file, indent=4)

def accessing_links():
    # Check if the links file exists
    if os.path.exists(link_file):
        with open(link_file, 'r') as file:
            data = json.load(file)

            # Iterate over each link in the file
            for link in data:
                article_url = link['link']
                summary = send_to_groq(article_url)
                if summary:
                    append_to_summaries_json(article_url, summary)

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

    # Send a POST request to the AI API
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
        # Assuming AI response is in the format "Title: <title>\n\nSummary: <summary>"
        title, summary = ai_response.split('\n\n', 1)
        return {"title": title.replace("Title: ", ""), "summary": summary.replace("Summary: ", "")}
    else:
        print("Error:", response.json())
        return None

def append_to_summaries_json(article_url, ai_response):
    # Create a dictionary with the article URL and AI response
    summary_data = {'source': article_url, 'data': ai_response}
    # Check if the summary file exists
    if os.path.exists(summary_file):
        with open(summary_file, 'r+') as file:
            try:
                # Load existing summaries from the file
                array_of_sum = json.load(file)
            except json.JSONDecodeError:
                # Initialize an empty list if the file is empty or contains invalid JSON
                array_of_sum = []
            # Append the new summary to the list
            array_of_sum.append(summary_data)
            # Seek to the beginning of the file
            file.seek(0)
            # Write the updated list back to the file with indentation
            json.dump(array_of_sum, file, indent=4)
    else:
        # Create a new file and write the new summary to it
        with open(summary_file, 'w') as file:
            json.dump([summary_data], file, indent=4)

# Run the main function
main()