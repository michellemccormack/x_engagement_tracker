"""
Apify Twitter scraper integration for X engagement tracking.
Uses Apify's tweet-scraper actor to get reliable Twitter data.
"""

import asyncio
import os
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class ApifyTwitterScraper:
    """Scraper for Twitter data using Apify's tweet-scraper actor."""
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Apify scraper.
        
        Args:
            api_token: Apify API token. If not provided, will use APIFY_API_TOKEN env var.
        """
        self.api_token = api_token or os.getenv('APIFY_API_TOKEN')
        if not self.api_token:
            raise ValueError("Apify API token is required. Set APIFY_API_TOKEN environment variable.")
        
        self.actor_id = "apidojo/tweet-scraper"
        self.base_url = "https://api.apify.com/v2"
    
    async def scrape_twitter_engagement(self, handles: List[str]) -> Dict[str, Any]:
        """
        Scrape Twitter engagement data for multiple handles using Apify API.
        
        Args:
            handles: List of Twitter handles (without @)
            
        Returns:
            Dictionary containing engagement analysis results
        """
        try:
            print(f"Scraping engagement data for {len(handles)} handles: {handles}")
            
            TWEETS_PER_HANDLE = 25
            max_items = len(handles) * TWEETS_PER_HANDLE
            
            async with aiohttp.ClientSession() as session:
                # Start the Apify scraper
                run_url = f"{self.base_url}/acts/{self.actor_id.replace('/', '~')}/runs?token={self.api_token}"
                
                # CORRECT FORMAT: Use searchTerms with "from:handle" syntax
                search_terms = [f"from:{handle}" for handle in handles]
                run_payload = {
                    "searchTerms": search_terms,  # ← CHANGED: Use searchTerms instead of handles
                    "tweetsDesired": max_items,
                    "sortBy": "Latest",
                    "addUserInfo": True  # ← ADD THIS to get follower counts
                }
                
                print(f"Search terms: {search_terms}")
                print(f"Max items: {max_items}")
                
                async with session.post(run_url, json=run_payload) as response:
                    if response.status != 201:
                        error_text = await response.text()
                        raise Exception(f"Failed to start Apify run: {response.status} - {error_text}")
                    
                    run_data = await response.json()
                    run_id = run_data['data']['id']
                
                print(f"Apify run started with ID: {run_id}")
                
                # Poll until the scraper finishes
                tweets = None
                attempts = 0
                max_attempts = 60  # 2 minutes max wait
                
                while attempts < max_attempts:
                    status_url = f"{self.base_url}/acts/{self.actor_id.replace('/', '~')}/runs/{run_id}?token={self.api_token}"
                    
                    async with session.get(status_url) as status_response:
                        status_data = await status_response.json()
                        status = status_data['data']['status']
                        print(f"Attempt {attempts + 1}: {status}")
                        
                        if status == 'SUCCEEDED':
                            dataset_id = status_data['data']['defaultDatasetId']
                            
                            # Get the scraped tweets
                            data_url = f"{self.base_url}/datasets/{dataset_id}/items?token={self.api_token}"
                            
                            async with session.get(data_url) as data_response:
                                tweets = await data_response.json()
                            
                            print(f"Retrieved {len(tweets)} tweets")
                            
                            if len(tweets) == 0:
                                raise Exception("No tweets found. Handles may be invalid or have no tweets.")
                            
                            break
                        elif status == 'FAILED':
                            error_msg = status_data['data'].get('statusMessage', 'Unknown')
                            raise Exception(f"Scraper failed: {error_msg}")
                    
                    await asyncio.sleep(3)  # Wait 3 seconds instead of 2
                    attempts += 1
                
                if not tweets:
                    raise Exception("Scraper timeout - took too long")
                
                # Calculate engagement rates
                return self._calculate_engagement_rates(tweets, handles)
                
        except Exception as e:
            print(f"Error scraping engagement data: {str(e)}")
            print("Falling back to demo data for demonstration purposes")
            return self._generate_demo_results(handles)
    
    def _calculate_engagement_rates(self, tweets: List[Dict], handles: List[str] = None) -> Dict[str, Any]:
        """Calculate engagement rates from scraped tweets."""
        print(f"Processing {len(tweets)} tweets")
        
        # Check if we got demo data
        if tweets and tweets[0].get('demo'):
            print("Received demo data from Apify - generating realistic mock data for demonstration")
            return self._generate_demo_results(handles)
        
        # Debug: Print first tweet structure
        if tweets:
            print("Sample tweet structure:")
            print(json.dumps(tweets[0], indent=2)[:500] + "...")
        
        user_stats = {}
        
        # Group tweets by user handle
        for tweet in tweets:
            # Try different possible field names for the author
            author = tweet.get('author') or tweet.get('user') or {}
            handle = author.get('userName') or author.get('username') or author.get('screen_name')
            
            if not handle:
                print(f"No handle found in tweet: {tweet.get('id', 'unknown')}")
                continue
            
            if handle not in user_stats:
                user_stats[handle] = {
                    'handle': handle,
                    'name': author.get('name', author.get('displayName', handle)),
                    'followers': author.get('followers', author.get('followersCount', 0)),
                    'tweets': [],
                    'totalLikes': 0,
                    'totalRetweets': 0,
                    'totalReplies': 0
                }
            
            user_stats[handle]['tweets'].append(tweet)
            
            # Try different possible field names for engagement metrics
            likes = tweet.get('likes') or tweet.get('favoriteCount') or tweet.get('likeCount') or 0
            retweets = tweet.get('retweets') or tweet.get('retweetCount') or tweet.get('shareCount') or 0
            replies = tweet.get('replies') or tweet.get('replyCount') or tweet.get('commentCount') or 0
            
            user_stats[handle]['totalLikes'] += likes
            user_stats[handle]['totalRetweets'] += retweets
            user_stats[handle]['totalReplies'] += replies
            
            print(f"Tweet from @{handle}: {likes} likes, {retweets} retweets, {replies} replies")
        
        # Calculate engagement rate for each user
        results = []
        for user in user_stats.values():
            tweet_count = len(user['tweets'])
            total_engagements = user['totalLikes'] + user['totalRetweets'] + user['totalReplies']
            
            # Engagement Rate = (Total Engagements) / (Followers × Tweets) × 100
            engagement_rate = 0
            if tweet_count > 0 and user['followers'] > 0:
                engagement_rate = (total_engagements / (user['followers'] * tweet_count)) * 100
            
            results.append({
                'handle': user['handle'],
                'name': user['name'],
                'followers': user['followers'],
                'tweetsAnalyzed': tweet_count,
                'totalLikes': user['totalLikes'],
                'totalRetweets': user['totalRetweets'],
                'totalReplies': user['totalReplies'],
                'totalEngagements': total_engagements,
                'engagementRate': round(engagement_rate, 2),
                'avgLikesPerTweet': round(user['totalLikes'] / tweet_count, 1) if tweet_count > 0 else 0,
                'avgRetweetsPerTweet': round(user['totalRetweets'] / tweet_count, 1) if tweet_count > 0 else 0,
                'avgRepliesPerTweet': round(user['totalReplies'] / tweet_count, 1) if tweet_count > 0 else 0
            })
        
        # Sort by engagement rate (highest first)
        results.sort(key=lambda x: x['engagementRate'], reverse=True)
        
        return {
            'results': results,
            'winner': results[0] if results else None,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_demo_results(self, original_handles: List[str] = None) -> Dict[str, Any]:
        """Generate realistic demo results when Apify returns demo data."""
        import random
        
        # Use original handles if provided, otherwise fall back to demo handles
        if original_handles:
            demo_handles = original_handles[:3]  # Use the actual handles entered
        else:
            demo_handles = ['elonmusk', 'NASA', 'OpenAI', 'tim_cook', 'sundarpichai']
        
        results = []
        for i, handle in enumerate(demo_handles):  # Use all provided handles
            # Generate realistic engagement data
            followers = random.randint(1000000, 50000000)  # 1M to 50M followers
            tweets_analyzed = random.randint(20, 25)
            
            # Base engagement varies by handle
            if handle == 'elonmusk':
                base_engagement = random.randint(50000, 200000)
            elif handle == 'NASA':
                base_engagement = random.randint(10000, 50000)
            else:
                base_engagement = random.randint(5000, 25000)
            
            total_likes = base_engagement * tweets_analyzed
            total_retweets = total_likes // 10
            total_replies = total_likes // 20
            total_engagements = total_likes + total_retweets + total_replies
            
            # Calculate engagement rate
            engagement_rate = (total_engagements / (followers * tweets_analyzed)) * 100
            
            results.append({
                'handle': handle,
                'name': handle.title(),
                'followers': followers,
                'tweetsAnalyzed': tweets_analyzed,
                'totalLikes': total_likes,
                'totalRetweets': total_retweets,
                'totalReplies': total_replies,
                'totalEngagements': total_engagements,
                'engagementRate': round(engagement_rate, 2),
                'avgLikesPerTweet': round(total_likes / tweets_analyzed, 1),
                'avgRetweetsPerTweet': round(total_retweets / tweets_analyzed, 1),
                'avgRepliesPerTweet': round(total_replies / tweets_analyzed, 1)
            })
        
        # Sort by engagement rate (highest first)
        results.sort(key=lambda x: x['engagementRate'], reverse=True)
        
        return {
            'results': results,
            'winner': results[0] if results else None,
            'timestamp': datetime.now().isoformat(),
            'demo_note': '⚠️ DEMO DATA ONLY - All numbers are fake! Follower counts, engagement rates, and metrics are randomly generated for demonstration purposes. To get real Twitter data, upgrade to Apify Pro ($40/month) or use Twitter API directly.',
            'disclaimer': 'This is a prototype/demo system. All data shown is simulated and not real Twitter data.'
        }
    
    async def scrape_multiple_users(self, usernames: List[str], max_tweets: int = 25) -> List[Dict[str, Any]]:
        """
        Scrape tweets for multiple Twitter users.
        
        Args:
            usernames: List of Twitter usernames (without @)
            max_tweets: Maximum number of tweets per user
            
        Returns:
            List of user data dictionaries
        """
        results = []
        
        for username in usernames:
            try:
                user_data = await self.scrape_user_tweets(username, max_tweets)
                results.append(user_data)
            except Exception as e:
                print(f"Failed to scrape @{username}: {str(e)}")
                results.append({
                    'username': username,
                    'followers': 0,
                    'tweets': [],
                    'error': str(e),
                    'scraped_at': datetime.now().isoformat()
                })
        
        return results
    
    def calculate_engagement_rate(self, user_data: Dict[str, Any]) -> float:
        """
        Calculate engagement rate for a user.
        
        Formula: (likes + retweets + replies) / (followers × tweets) × 100
        
        Args:
            user_data: User data dictionary from scraping
            
        Returns:
            Engagement rate as a percentage
        """
        try:
            tweets = user_data.get('tweets', [])
            followers = user_data.get('followers', 0)
            
            if not tweets or followers == 0:
                return 0.0
            
            # Calculate total engagement across all tweets
            total_engagement = 0
            for tweet in tweets:
                likes = tweet.get('likes', 0)
                retweets = tweet.get('retweets', 0)
                replies = tweet.get('replies', 0)
                total_engagement += likes + retweets + replies
            
            # Calculate engagement rate
            engagement_rate = (total_engagement / (followers * len(tweets))) * 100
            
            return round(engagement_rate, 4)
            
        except Exception as e:
            print(f"Error calculating engagement rate: {str(e)}")
            return 0.0
    
    def get_user_stats(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive stats for a user."""
        tweets = user_data.get('tweets', [])
        
        if not tweets:
            return {
                'total_tweets': 0,
                'total_likes': 0,
                'total_retweets': 0,
                'total_replies': 0,
                'avg_likes_per_tweet': 0,
                'avg_retweets_per_tweet': 0,
                'avg_replies_per_tweet': 0,
                'engagement_rate': 0.0
            }
        
        total_likes = sum(tweet.get('likes', 0) for tweet in tweets)
        total_retweets = sum(tweet.get('retweets', 0) for tweet in tweets)
        total_replies = sum(tweet.get('replies', 0) for tweet in tweets)
        
        return {
            'total_tweets': len(tweets),
            'total_likes': total_likes,
            'total_retweets': total_retweets,
            'total_replies': total_replies,
            'avg_likes_per_tweet': round(total_likes / len(tweets), 2),
            'avg_retweets_per_tweet': round(total_retweets / len(tweets), 2),
            'avg_replies_per_tweet': round(total_replies / len(tweets), 2),
            'engagement_rate': self.calculate_engagement_rate(user_data)
        }
