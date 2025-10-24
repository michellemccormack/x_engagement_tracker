# 💻 Paste into Codex
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apify_scraper import ApifyTwitterScraper
from dotenv import load_dotenv
import os
from typing import List

load_dotenv()

app = FastAPI(title="X Engagement Tracker")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Apify scraper
try:
    scraper = ApifyTwitterScraper()
    print("Apify scraper initialized successfully")
except ValueError as e:
    print(f"Warning: {e}")
    scraper = None
except Exception as e:
    print(f"Error initializing Apify scraper: {e}")
    scraper = None

@app.post("/api/compare-engagement")
async def compare_engagement(request: dict):
    """
    Compare engagement rates of 2-3 Twitter handles.
    
    Request body:
    {
        "handles": ["elonmusk", "tim_cook", "sundarpichai"]
    }
    
    Returns:
        Engagement comparison results with winner
    """
    if not scraper:
        raise HTTPException(status_code=500, detail="Apify API token not configured")
    
    try:
        handles = request.get('handles', [])
        
        # Validation
        if not handles or not isinstance(handles, list) or len(handles) == 0:
            raise HTTPException(status_code=400, detail="Please provide an array of Twitter handles")
        
        if len(handles) < 2:
            raise HTTPException(status_code=400, detail="Minimum 2 handles required")
        
        if len(handles) > 3:
            raise HTTPException(status_code=400, detail="Maximum 3 handles allowed")
        
        # Clean handles (remove @ if included)
        clean_handles = [h.replace('@', '').strip() for h in handles]
        
        # Scrape engagement data
        engagement_data = await scraper.scrape_twitter_engagement(clean_handles)
        
        if engagement_data.get('error'):
            raise HTTPException(status_code=500, detail=engagement_data['error'])
        
        return {
            "success": True,
            "data": engagement_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in compare_engagement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/compare")
async def compare_get(handles: str):
    """
    GET endpoint for comparing handles (comma-separated).
    
    Args:
        handles: Comma-separated list of Twitter handles (e.g., "elonmusk,tim_cook")
        
    Returns:
        Comparison results with engagement rates and rankings
    """
    if not scraper:
        raise HTTPException(status_code=500, detail="Apify API token not configured")
    
    # Parse handles
    handle_list = [h.strip().lstrip("@") for h in handles.split(",") if h.strip()]
    
    if len(handle_list) < 2:
        raise HTTPException(status_code=400, detail="Minimum 2 handles required")
    if len(handle_list) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 handles allowed")
    
    try:
        # Scrape engagement data
        engagement_data = await scraper.scrape_twitter_engagement(handle_list)
        
        if engagement_data.get('error'):
            raise HTTPException(status_code=500, detail=engagement_data['error'])
        
        return {
            "success": True,
            "data": engagement_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/api")
def api_info():
    return {
        "message": "X Engagement Tracker API running",
        "endpoints": {
            "compare_post": "POST /api/compare-engagement",
            "compare_get": "GET /compare?handles=handle1,handle2,handle3",
            "docs": "/docs",
            "web_interface": "/"
        },
        "engagement_formula": "(likes + retweets + replies) / (followers × tweets) × 100",
        "cost_info": "3 handles × 25 tweets = 75 tweets = $0.03 per comparison"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

