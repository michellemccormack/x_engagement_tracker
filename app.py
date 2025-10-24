"""
FastAPI application for X (Twitter) engagement tracking.
Main API endpoints for the engagement tracker service.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

from playwright_scraper import XScraper
from vision_parser import VisionParser
from calculations import EngagementCalculator

app = FastAPI(
    title="X Engagement Tracker",
    description="Track and analyze X (Twitter) engagement metrics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
scraper = XScraper()
vision_parser = VisionParser()
calculator = EngagementCalculator()

class PostAnalysisRequest(BaseModel):
    post_url: str
    username: Optional[str] = None

class PostAnalysisResponse(BaseModel):
    post_url: str
    username: str
    content: str
    engagement_metrics: Dict[str, Any]
    analysis_timestamp: datetime
    comparison_data: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "X Engagement Tracker API", "status": "running"}

@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "scraper": "ready",
            "vision_parser": "ready",
            "calculator": "ready"
        }
    }

@app.post("/analyze-post", response_model=PostAnalysisResponse)
async def analyze_post(request: PostAnalysisRequest):
    """
    Analyze a specific X post for engagement metrics.
    
    Args:
        request: PostAnalysisRequest containing post URL and optional username
        
    Returns:
        PostAnalysisResponse with engagement data and analysis
    """
    try:
        # Scrape the post data
        post_data = await scraper.scrape_post(request.post_url)
        
        if not post_data:
            raise HTTPException(status_code=404, detail="Post not found or could not be scraped")
        
        # Parse engagement metrics using vision
        engagement_metrics = await vision_parser.parse_engagement_metrics(post_data)
        
        # Calculate engagement score and comparisons
        analysis = calculator.analyze_engagement(engagement_metrics)
        
        # Get comparison data if username is provided
        comparison_data = None
        if request.username:
            comparison_data = await calculator.get_user_comparison(request.username)
        
        return PostAnalysisResponse(
            post_url=request.post_url,
            username=post_data.get('username', ''),
            content=post_data.get('content', ''),
            engagement_metrics=engagement_metrics,
            analysis_timestamp=datetime.now(),
            comparison_data=comparison_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/user/{username}/stats")
async def get_user_stats(username: str):
    """
    Get engagement statistics for a specific user.
    
    Args:
        username: X username to analyze
        
    Returns:
        User engagement statistics and trends
    """
    try:
        stats = await calculator.get_user_stats(username)
        return {
            "username": username,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user stats: {str(e)}")

@app.get("/trending")
async def get_trending_analysis():
    """
    Get trending engagement analysis across the platform.
    
    Returns:
        Trending topics and engagement patterns
    """
    try:
        trending_data = await calculator.get_trending_analysis()
        return {
            "trending": trending_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

