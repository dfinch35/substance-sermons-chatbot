import os
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.web import BeautifulSoupWebReader
from llama_index.core import Document
import requests
from bs4 import BeautifulSoup

load_dotenv()

def scrape_blog_urls():
    """Scrape all post URLs from https://www.peterhaas.org/blog/"""
    url = "https://www.peterhaas.org/blog/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    posts = []
    for h3 in soup.find_all("h3"):  # titles are in h3
        a = h3.find("a")
        if a:
            title = a.text.strip()
            link = a["href"]
            if link.startswith("/"):
                link = "https://www.peterhaas.org" + link
            posts.append({"title": title, "url": link})
    return posts

def load_blogs():
    reader = BeautifulSoupWebReader()
    posts = scrape_blog_urls()
    documents = []
    for post in posts:
        print(f"Loading: {post['title']}")
        docs = reader.load_data(urls=[post["url"]])
        for doc in docs:
            doc.metadata["source"] = post["url"]
            doc.metadata["title"] = post["title"]
            doc.metadata["type"] = "blog"
        documents.extend(docs)
    return documents

if __name__ == "__main__":
    docs = load_blogs()
    # Optional: save raw text for inspection
    os.makedirs("data/blogs", exist_ok=True)
    for i, doc in enumerate(docs):
        with open(f"data/blogs/post_{i}.txt", "w") as f:
            f.write(doc.text)
    print(f"✅ Loaded {len(docs)} blog documents")
