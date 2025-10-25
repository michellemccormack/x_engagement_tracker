import os
import requests
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class RapidAPIClient:
    """Client for XScraper API via RapidAPI"""
    
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.host = os.getenv("RAPIDAPI_HOST", "xscraper.p.rapidapi.com")
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
            
            url = f"{self.base_url}/user/profile"
            params = {"username": username}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Transform to match expected format
            if data.get("success", False):
                profile_data = data.get("data", {})
                return {
                    "id": profile_data.get("id"),
                    "username": profile_data.get("username"),
                    "name": profile_data.get("name"),
                    "followers_count": profile_data.get("followers_count", 0),
                    "following_count": profile_data.get("following_count", 0),
                    "tweet_count": profile_data.get("tweet_count", 0),
                    "verified": profile_data.get("verified", False),
                    "profile_image_url": profile_data.get("profile_image_url"),
                    "description": profile_data.get("description", ""),
                    "created_at": profile_data.get("created_at")
                }
            return None
            
        except Exception as e:
            print(f"Error fetching user profile for {username}: {e}")
            return None
    
    async def get_user_tweets(self, username: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get user's recent tweets"""
        if not self.is_configured():
            return []
            
        try:
            # Remove @ if present
            username = username.lstrip('@')
            
            url = f"{self.base_url}/user/tweets"
            params = {
                "username": username,
                "limit": min(limit, 100)  # API limit
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Transform to match expected format
            if data.get("success", False):
                tweets_data = data.get("data", [])
                tweets = []
                
                for tweet in tweets_data:
                    tweets.append({
                        "id": tweet.get("id"),
                        "text": tweet.get("text", ""),
                        "created_at": tweet.get("created_at"),
                        "public_metrics": {
                            "like_count": tweet.get("like_count", 0),
                            "retweet_count": tweet.get("retweet_count", 0),
                            "reply_count": tweet.get("reply_count", 0),
                            "quote_count": tweet.get("quote_count", 0)
                        },
                        "author_id": tweet.get("author_id"),
                        "conversation_id": tweet.get("conversation_id"),
                        "referenced_tweets": tweet.get("referenced_tweets", [])
                    })
                
                return tweets
            return []
            
        except Exception as e:
            print(f"Error fetching tweets for {username}: {e}")
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
        if not self.is_configured():
            return {
                "success": False,
                "error": "RapidAPI credentials not configured"
            }
        
        try:
            # Get stats for all handles
            results = []
            for handle in handles:
                stats = await self.get_user_stats(handle)
                if stats:
                    results.append(stats)
            
            if not results:
                return {
                    "success": False,
                    "error": "No valid handles found"
                }
            
            # Find winner (highest engagement rate)
            winner = max(results, key=lambda x: x.get("engagement_rate", 0))
            
            return {
                "success": True,
                "data": {
                    "results": results,
                    "winner": winner,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
            
        except Exception as e:
            print(f"Error comparing handles: {e}")
            return {
                "success": False,
                "error": str(e)
            }
