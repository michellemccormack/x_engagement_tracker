from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from rapidapi_client import RapidAPIClient
from dotenv import load_dotenv
import os

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

# Initialize RapidAPI client
rapidapi_client = None
try:
    rapidapi_client = RapidAPIClient()
    if rapidapi_client.is_configured():
        print("RapidAPI client initialized successfully")
    else:
        print("RapidAPI credentials not configured - app will run in demo mode")
        rapidapi_client = None
except Exception as e:
    print(f"Warning: RapidAPI client failed to initialize: {e}")
    print("App will continue in demo mode")
    rapidapi_client = None

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
    # TEMPORARILY FORCE DEMO MODE - REMOVE THIS LATER
    handles = request.get('handles', [])
    return {
        "success": True,
        "data": {
            "results": [
                {
                    "handle": handle,
                    "name": handle.title(),
                    "followers": 1000000 + (hash(handle) % 10000000),
                    "tweetsAnalyzed": 25,
                    "totalLikes": 50000 + (hash(handle) % 100000),
                    "totalRetweets": 5000 + (hash(handle) % 10000),
                    "totalReplies": 2500 + (hash(handle) % 5000),
                    "totalEngagements": 57500 + (hash(handle) % 115000),
                    "engagementRate": round(0.05 + (hash(handle) % 10) / 100, 2),
                    "avgLikesPerTweet": 2000 + (hash(handle) % 4000),
                    "avgRetweetsPerTweet": 200 + (hash(handle) % 400),
                    "avgRepliesPerTweet": 100 + (hash(handle) % 200)
                } for handle in handles
            ],
            "winner": None,
            "timestamp": "2025-10-24T19:30:00Z",
            "demo_note": "🎯 DEMO MODE - This is simulated data for demonstration purposes. To get real Twitter data, configure your RapidAPI credentials."
        }
    }
    
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
        
        # Scrape engagement data using RapidAPI
        print(f"DEBUG: Calling compare_handles with: {clean_handles}")
        engagement_data = await rapidapi_client.compare_handles(clean_handles)
        print(f"DEBUG: compare_handles returned: {engagement_data}")
        
        if not engagement_data.get('success'):
            print(f"DEBUG: API call failed with error: {engagement_data.get('error')}")
            raise HTTPException(status_code=500, detail=engagement_data.get('error', 'Failed to fetch data'))
        
        return engagement_data
        
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
    if not rapidapi_client:
        raise HTTPException(status_code=500, detail="RapidAPI credentials not configured")
    
    # Parse handles
    handle_list = [h.strip().lstrip("@") for h in handles.split(",") if h.strip()]
    
    if len(handle_list) < 2:
        raise HTTPException(status_code=400, detail="Minimum 2 handles required")
    if len(handle_list) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 handles allowed")
    
    try:
        # Scrape engagement data using RapidAPI
        engagement_data = await rapidapi_client.compare_handles(handle_list)
        
        if not engagement_data.get('success'):
            raise HTTPException(status_code=500, detail=engagement_data.get('error', 'Failed to fetch data'))
        
        return engagement_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "message": "X Engagement Tracker is running"}

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
    print(f"PORT environment variable: {os.getenv('PORT')}")
    uvicorn.run(app, host="0.0.0.0", port=port)

