import json
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is missing from the .env file!")

# File Paths
src = "src.json"
link_file = "links.json"

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to my first API... News Sum"}

@app.post("/summarize")
def main():
    if not os.path.exists(src):
        raise HTTPException(status_code=400, detail="Source file not found.")

    try:
        with open(src, "r") as file:
            data = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        raise HTTPException(status_code=400, detail="Invalid or empty source file.")

    summaries = []
    for key, url in data.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "xml")
            get_links(soup)
        except requests.exceptions.RequestException as e:
            print(f"Unable to fetch URL for {key}:", e)
            continue

    summaries = accessing_links()
    return {"summaries": summaries}

def get_links(soup):
    """Extracts links from the RSS feed and stores them in a list."""
    items_in_rss = soup.find_all("item")
    if items_in_rss:
        stuff_in_items = []
        for item in items_in_rss:
            title = item.find("title").text if item.find("title") else "No title"
            link = item.find("link").text if item.find("link") else "No link"
            stuff_in_items.append({"title": title, "link": link})

        with open(link_file, "w") as file:
            json.dump(stuff_in_items, file, indent=4)

def accessing_links():
    """Reads links from link_file and summarizes each article."""
    summaries = []
    if os.path.exists(link_file):
        try:
            with open(link_file, "r") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            return []

        for link in data:
            article_url = link["link"]
            summary = send_to_groq(article_url)
            if summary:
                summaries.append({"source": article_url, "data": summary})

    return summaries

def send_to_groq(article_url):
    """Sends article URL to AI model and retrieves summary."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Summarize the article from this URL and return the title and summary."},
            {"role": "user", "content": f"Summarize this link: {article_url}"}
        ]
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        ai_response = response.json()["choices"][0]["message"]["content"]

        if "\n\n" in ai_response:
            title, summary = ai_response.split("\n\n", 1)
            return {"title": title.replace("Title: ", ""), "summary": summary.replace("Summary: ", "")}
        else:
            return {"summary": ai_response}

    except requests.exceptions.RequestException as e:
        print("Error contacting AI API:", e)
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
