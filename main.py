import json
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# File paths
link_file = "links.json"
src_file = "src.json"

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

@app.get("/summaries")
def get_summaries():
    """Fetches the summaries from the links."""
    try:
        summaries = accessing_links()
        return summaries
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
    """Fetches article summaries from Groq API and returns them."""
    summaries = []
    if os.path.exists(link_file):
        with open(link_file, "r") as file:
            data = json.load(file)
            for link in data:
                article_url = link["link"]
                summary = send_to_groq(article_url)
                if summary:
                    summaries.append(summary)
    return summaries

def send_to_groq(article_url):
    """Sends the article URL to Groq API for summarization."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Summarize the article from this URL and return the title, URL and summary as JSON."},
            {"role": "user", "content": f"Summarize this link: {article_url}"},
        ],
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        ai_response = response.json()["choices"][0]["message"]["content"]
        try:
            ai_response_json = json.loads(ai_response)
            title = ai_response_json.get("title", "No title")
            summary = ai_response_json.get("summary", "No summary")
            return {"title": title, "url": article_url, "summary": summary}
        except json.JSONDecodeError:
            print(ai_response)
            return None
    else:
        print("Error:", response.json())
        return None

# Ensure the script only runs when executed directly
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=3000)
