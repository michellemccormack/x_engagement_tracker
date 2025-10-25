import os
import requests
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class RapidAPIClient:
    """Client for XScraper API via RapidAPI"""
    
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.host = os.getenv("RAPIDAPI_HOST", "twitter-x-scraper-api.p.rapidapi.com")
        self.base_url = f"https://{self.host}"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host,
            "Content-Type": "application/json"
        }
        
    def is_configured(self) -> bool:
        """Check if API credentials are configured"""
        return bool(self.api_key and self.api_key != "your_rapidapi_key_here")
    
    async def get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        if not self.is_configured():
            return None
            
        try:
            # Remove @ if present
            username = username.lstrip('@')
            
            # Try the correct Twitter X Scraper API endpoints
            endpoints_to_try = [
                f"{self.base_url}/getProfile",
                f"{self.base_url}/profile",
                f"{self.base_url}/user/profile",
                f"{self.base_url}/users/{username}"
            ]
            
            response = None
            for url in endpoints_to_try:
                print(f"Trying endpoint: {url}")
                if "/users/" in url:
                    response = requests.get(url, headers=self.headers, timeout=30)
                else:
                    params = {"handle": username}  # Use 'handle' as per RapidAPI playground
                    response = requests.get(url, headers=self.headers, params=params, timeout=30)
                
                print(f"Response status: {response.status_code}")
                print(f"Response content: {response.text[:500]}")
                
                if response.status_code == 200:
                    print(f"SUCCESS with endpoint: {url}")
                    break
                else:
                    print(f"Failed with endpoint: {url}")
            
            if not response or response.status_code != 200:
                print("All endpoints failed")
                return None
            
            response.raise_for_status()
            
            data = response.json()
            print(f"Parsed JSON: {data}")
            
            # Handle the actual Twitter X Scraper API response format
            legacy = data.get("legacy", {})
            
            return {
                "id": data.get("rest_id"),
                "username": data.get("legacy", {}).get("screen_name", ""),
                "name": legacy.get("name", ""),
                "followers_count": legacy.get("followers_count", 0),
                "following_count": legacy.get("friends_count", 0),
                "tweet_count": legacy.get("statuses_count", 0),
                "verified": legacy.get("verified", False),
                "profile_image_url": legacy.get("profile_image_url_https", ""),
                "description": legacy.get("description", ""),
                "created_at": legacy.get("created_at")
            }
            
        except Exception as e:
            print(f"ERROR: Failed to fetch user profile for {username}: {e}")
            import traceback
            print(f"ERROR: Profile traceback: {traceback.format_exc()}")
            return None
    
    async def get_user_tweets(self, username: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get user's recent tweets"""
        if not self.is_configured():
            return []
            
        try:
            # Remove @ if present
            username = username.lstrip('@')
            
            # Try multiple possible endpoints for tweets
            endpoints_to_try = [
                f"{self.base_url}/getUserTweets",
                f"{self.base_url}/userTweets", 
                f"{self.base_url}/tweets",
                f"{self.base_url}/user/tweets",
                f"{self.base_url}/getTweets"
            ]
            
            response = None
            for url in endpoints_to_try:
                print(f"Trying tweet endpoint: {url}")
                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                print(f"Tweet endpoint response status: {response.status_code}")
                if response.status_code == 200:
                    print(f"SUCCESS with tweet endpoint: {url}")
                    break
                else:
                    print(f"Failed with tweet endpoint: {url}")
            
            if not response or response.status_code != 200:
                print("All tweet endpoints failed")
                return []
            
            url = endpoints_to_try[0]  # Keep original for logging
            params = {
                "handle": username,  # Use 'handle' as per RapidAPI playground
                "count": min(limit, 100)  # API limit
            }
            
            print(f"DEBUG: Calling getUserTweets with handle={username}, count={min(limit, 100)}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            print(f"DEBUG: getUserTweets response status: {response.status_code}")
            print(f"DEBUG: getUserTweets response: {response.text[:500]}")
            response.raise_for_status()
            
            data = response.json()
            print(f"DEBUG: getUserTweets parsed JSON: {data}")
            
            # Handle the actual Twitter X Scraper API response format
            tweets = []
            tweets_data = data.get("tweets", [])
            print(f"DEBUG: Found {len(tweets_data)} tweets")
            
            for tweet in tweets_data:
                legacy = tweet.get("legacy", {})
                
                tweets.append({
                    "id": legacy.get("id_str"),
                    "text": legacy.get("full_text", ""),
                    "created_at": legacy.get("created_at"),
                    "public_metrics": {
                        "like_count": legacy.get("favorite_count", 0),
                        "retweet_count": legacy.get("retweet_count", 0),
                        "reply_count": legacy.get("reply_count", 0),
                        "quote_count": legacy.get("quote_count", 0)
                    },
                    "author_id": legacy.get("user_id_str"),
                    "conversation_id": legacy.get("conversation_id_str"),
                    "referenced_tweets": []
                })
            
            return tweets
            
        except Exception as e:
            print(f"ERROR: Failed to fetch tweets for {username}: {e}")
            return []
    
    async def get_user_stats(self, username: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive user statistics"""
        if not self.is_configured():
            return None
            
        try:
            # Get profile and tweets
            profile = await self.get_user_profile(username)
            tweets = await self.get_user_tweets(username, 25)
            
            if not profile:
                return None
            
            # Calculate engagement metrics
            total_likes = sum(tweet.get("public_metrics", {}).get("like_count", 0) for tweet in tweets)
            total_retweets = sum(tweet.get("public_metrics", {}).get("retweet_count", 0) for tweet in tweets)
            total_replies = sum(tweet.get("public_metrics", {}).get("reply_count", 0) for tweet in tweets)
            total_engagements = total_likes + total_retweets + total_replies
            
            # Calculate engagement rate
            followers = profile.get("followers_count", 1)
            tweets_analyzed = len(tweets)
            
            if tweets_analyzed > 0 and followers > 0:
                engagement_rate = (total_engagements / (followers * tweets_analyzed)) * 100
            else:
                engagement_rate = 0
            
            return {
                "handle": username,
                "name": profile.get("name", username),
                "followers": followers,
                "tweetsAnalyzed": tweets_analyzed,
                "totalLikes": total_likes,
                "totalRetweets": total_retweets,
                "totalReplies": total_replies,
                "totalEngagements": total_engagements,
                "engagementRate": round(engagement_rate, 2),
                "avgLikesPerTweet": round(total_likes / max(tweets_analyzed, 1), 0),
                "avgRetweetsPerTweet": round(total_retweets / max(tweets_analyzed, 1), 0),
                "avgRepliesPerTweet": round(total_replies / max(tweets_analyzed, 1), 0),
                "verified": profile.get("verified", False),
                "profile_image": profile.get("profile_image_url"),
                "description": profile.get("description", ""),
                "tweets": tweets
            }
            
        except Exception as e:
            print(f"Error getting stats for {username}: {e}")
            return None
    
    async def compare_handles(self, handles: List[str]) -> Dict[str, Any]:
        """Compare multiple handles and return results"""
        print(f"DEBUG: compare_handles called with handles: {handles}")
        
        if not self.is_configured():
            print("DEBUG: RapidAPI not configured")
            return {
                "success": False,
                "error": "RapidAPI credentials not configured"
            }
        
        try:
            # Get stats for all handles
            results = []
            for i, handle in enumerate(handles):
                print(f"DEBUG: Processing handle {i+1}/{len(handles)}: {handle}")
                stats = await self.get_user_stats(handle)
                if stats:
                    print(f"DEBUG: Successfully got stats for {handle}: {stats}")
                    results.append(stats)
                else:
                    print(f"DEBUG: Failed to get stats for {handle}")
            
            print(f"DEBUG: Total results collected: {len(results)}")
            
            if not results:
                print("DEBUG: No valid results found")
                return {
                    "success": False,
                    "error": "No valid handles found"
                }
            
            # Find winner (highest engagement rate)
            winner = max(results, key=lambda x: x.get("engagementRate", 0))
            print(f"DEBUG: Winner determined: {winner.get('handle')} with {winner.get('engagementRate')}% engagement rate")
            
            return {
                "success": True,
                "data": {
                    "results": results,
                    "winner": winner,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
            
        except Exception as e:
            print(f"ERROR: Exception in compare_handles: {e}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
