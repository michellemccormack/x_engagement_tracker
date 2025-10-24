# 💻 Paste into Codex
from fastapi import FastAPI, Query
from playwright_scraper import scrape_tweets
from vision_parser import extract_engagements
from calculations import compute_comparison
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="X Engagement Tracker")

@app.get("/compare")
async def compare(handles: str = Query(..., description="Comma-separated X handles")):
    handle_list = [h.strip().lstrip("@") for h in handles.split(",") if h.strip()]
    results = []

    for handle in handle_list:
        print(f"Scraping @{handle}...")
        screenshots = await scrape_tweets(handle)
        data = await extract_engagements(handle, screenshots)
        results.append(data)

    comparison = compute_comparison(results)
    return {"results": results, "comparison": comparison}

@app.get("/")
def home():
    return {"message": "X Engagement Tracker API running. Use /compare?handles=@handle1,@handle2"}

