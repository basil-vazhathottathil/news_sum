import json
import os
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# File paths
link_file = "links.json"
src_file = "src.json"
summary_file = "summary.json"

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is running!"}

@app.get("/run")
def run_script():
    """Runs the main script."""
    try:
        main()
        return {"status": "success", "message": "Script executed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    """Main script execution."""
    if os.path.exists(src_file):
        with open(src_file, "r") as file:
            data = json.load(file)
            for key, url in data.items():
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "xml")
                    get_links(soup)
                except requests.exceptions.RequestException as e:
                    print(f"Unable to fetch URL for {key}:", e)
    else:
        print("The file is not at the given address")

    accessing_links()

def get_links(soup):
    """Extracts article links from RSS XML and saves them to a JSON file."""
    items_in_rss = soup.find_all("item")
    if items_in_rss:
        extracted_items = []
        for item in items_in_rss:
            title = item.find("title").text if item.find("title") else "No title"
            link = item.find("link").text if item.find("link") else "No link"
            extracted_items.append({"title": title, "link": link})

        with open(link_file, "w") as file:
            json.dump(extracted_items, file, indent=4)

def accessing_links():
    """Fetches article summaries from Groq API."""
    if os.path.exists(link_file):
        with open(link_file, "r") as file:
            data = json.load(file)
            for link in data:
                article_url = link["link"]
                summary = send_to_groq(article_url)
                if summary:
                    append_to_summaries_json(article_url, summary)

def send_to_groq(article_url):
    """Sends the article URL to Groq API for summarization."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Summarize the article from this URL and return the title and summary."},
            {"role": "user", "content": f"Summarize this link: {article_url}"},
        ],
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
        # Improved AI response parsing
        title_match = re.search(r"Title:\s*(.*?)\n", ai_response, re.IGNORECASE)
        summary_match = re.search(r"Summary:\s*(.*)", ai_response, re.IGNORECASE | re.DOTALL)

        title = title_match.group(1) if title_match else "Untitled"
        summary = summary_match.group(1) if summary_match else "No summary available."

        return {"title": title.strip(), "summary": summary.strip()}
    else:
        print("Error:", response.json())
        return None

def append_to_summaries_json(article_url, ai_response):
    """Stores AI-generated summaries into a JSON file."""
    summary_data = {"source": article_url, "data": ai_response}

    if os.path.exists(summary_file):
        with open(summary_file, "r+") as file:
            try:
                array_of_summaries = json.load(file)
            except json.JSONDecodeError:
                array_of_summaries = []
            array_of_summaries.append(summary_data)
            file.seek(0)
            json.dump(array_of_summaries, file, indent=4)
    else:
        with open(summary_file, "w") as file:
            json.dump([summary_data], file, indent=4)

# Ensure the script only runs when executed directly
if __name__ == "__main__":
    main()
