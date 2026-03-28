from llama_index.readers.youtube_transcript import YoutubeTranscriptReader
from llama_index.core import Document
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def load_sermons():
    """
    Load Substance Church sermons from 2025 and 2026.
    Each entry includes title, URL, and approximate sermon date for metadata.
    Add new sermons here as they are uploaded.
    """
    # Sermon list with dates (format: YYYY-MM-DD) for accurate metadata
    sermons = [
        # === 2026 Sermons ===
        {
            "title": "The Power of Holy Ground",
            "url": "https://www.youtube.com/watch?v=YRKTLS_GWnI",
            "date": "2026-03-05"   # First Wednesday March 2026
        },
        {
            "title": "Metamorphosis Process | Discover Your Identity Part 4",
            "url": "https://www.youtube.com/watch?v=EHve6ZKr-JE",
            "date": "2026-03-08"
        },
        {
            "title": "False Fathers vs Real | Discover Your Identity Part 2",
            "url": "https://www.youtube.com/watch?v=JcaaEGMkeTU",
            "date": "2026-02-16"
        },
        {
            "title": "Removing Scars | Discover Your Identity Part 1",
            "url": "https://www.youtube.com/watch?v=dOyJvLQfuXM",
            "date": "2026-02-08"
        },
        {
            "title": "Turning Bitter to Sweet",
            "url": "https://www.youtube.com/watch?v=UmZOx-EtEDE",
            "date": "2026-02-05"   # First Wednesday February 2026
        },
        {
            "title": "Prayer & Fasting: Spiritual Disciplines Panel",
            "url": "https://www.youtube.com/watch?v=QK8RIypvw1Y",
            "date": "2026-01-08"   # Ties directly to the January 2026 blog post
        },
        {
            "title": "Fasting for the Mind of Christ",
            "url": "https://www.youtube.com/watch?v=MP8Zw-I_veY",
            "date": "2026-01-11"
        },

        # === 2025 Sermons (selected key messages) ===
        {
            "title": "God's Plan to Change the World",
            "url": "https://www.youtube.com/watch?v=oUXhC8skUE4",
            "date": "2025-11-06"   # First Wednesday November 2025
        },
        {
            "title": "The 90-Day Challenge",
            "url": "https://www.youtube.com/watch?v=h0tT4kRNVnA",
            "date": "2025-06-21" # DJF picked a Sunday date
        },
        {
            "title": "Prayer & Unity",
            "url": "https://www.youtube.com/watch?v=Y8SJ8qOFjRo",
            "date": "2025-02-16" # DJF picked a Sunday date
        },
        {
            "title": "Why are You Crying? | Easter 2025",
            "url": "https://www.youtube.com/watch?v=hhIXv5eCzMs",
            "date": "2025-04-20"   # Approximate Easter 2025
        },
        # Add more 2025 sermons here as needed (e.g. from "Recent Messages" playlist)
    ]

    print(f"Loading {len(sermons)} sermons (2025 + 2026)...")

    loader = YoutubeTranscriptReader()
    documents = []

    for sermon in sermons:
        print(f"  Loading: {sermon['title']} ({sermon['date']})")
        try:
            loaded_docs = loader.load_data(video_urls=[sermon["url"]])
            
            for doc in loaded_docs:
                # Add rich metadata for better retrieval and filtering
                doc.metadata["type"] = "sermon"
                doc.metadata["title"] = sermon["title"]
                doc.metadata["date"] = sermon["date"]
                doc.metadata["year"] = sermon["date"][:4]
                doc.metadata["source_url"] = sermon["url"]
                
                # Optional: parse date for potential future date-based filtering
                try:
                    doc.metadata["date_obj"] = datetime.strptime(sermon["date"], "%Y-%m-%d")
                except:
                    pass
                
                documents.append(doc)
            
        except Exception as e:
            print(f"    ⚠️  Failed to load {sermon['title']}: {e}")

    # Save raw transcripts for backup and inspection
    os.makedirs("data/sermons", exist_ok=True)
    for i, doc in enumerate(documents):
        title = doc.metadata.get("title", f"sermon_{i}")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)[:100]
        date_str = doc.metadata.get("date", "unknown")
        filename = f"{date_str}_{safe_title}.txt"
        
        with open(f"data/sermons/{filename}", "w", encoding="utf-8") as f:
            f.write(doc.text)
        print(f"  Saved: {filename}")

    print(f"✅ Successfully loaded {len(documents)} sermon transcripts (2025 + 2026).")
    return documents

if __name__ == "__main__":
    docs = load_sermons()
