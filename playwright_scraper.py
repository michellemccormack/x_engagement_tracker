"""
Playwright-based web scraper for X (Twitter) posts.
Handles browser automation and data extraction.
"""

import asyncio
import os
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page
import time
import json
from datetime import datetime

class XScraper:
    """Scraper for X (Twitter) posts using Playwright."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the browser and page."""
        if self.is_initialized:
            return
            
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create a new context with realistic user agent
        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        self.page = await context.new_page()
        
        # Set up request interception to block unnecessary resources
        await self.page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf,eot}", lambda route: route.abort())
        
        self.is_initialized = True
    
    async def scrape_post(self, post_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a specific X post for engagement data.
        
        Args:
            post_url: URL of the X post to scrape
            
        Returns:
            Dictionary containing post data and engagement metrics
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Navigate to the post
            await self.page.goto(post_url, wait_until='networkidle', timeout=30000)
            
            # Wait for the post content to load
            await self.page.wait_for_selector('[data-testid="tweet"]', timeout=10000)
            
            # Take a screenshot for vision analysis
            screenshot_path = f"/tmp/post_screenshot_{int(time.time())}.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            
            # Extract basic post information
            post_data = await self._extract_post_data()
            post_data['screenshot_path'] = screenshot_path
            post_data['url'] = post_url
            
            return post_data
            
        except Exception as e:
            print(f"Error scraping post {post_url}: {str(e)}")
            return None
    
    async def _extract_post_data(self) -> Dict[str, Any]:
        """Extract basic post data from the page."""
        try:
            # Wait for the tweet to be fully loaded
            await self.page.wait_for_selector('[data-testid="tweet"]', timeout=5000)
            
            # Extract username
            username_element = await self.page.query_selector('[data-testid="User-Name"] a')
            username = await username_element.inner_text() if username_element else "Unknown"
            
            # Extract post content
            content_element = await self.page.query_selector('[data-testid="tweetText"]')
            content = await content_element.inner_text() if content_element else ""
            
            # Extract timestamp
            time_element = await self.page.query_selector('time')
            timestamp = await time_element.get_attribute('datetime') if time_element else None
            
            # Extract engagement metrics (these might be in different formats)
            engagement_data = await self._extract_engagement_metrics()
            
            return {
                'username': username.strip(),
                'content': content.strip(),
                'timestamp': timestamp,
                'engagement_data': engagement_data,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting post data: {str(e)}")
            return {
                'username': 'Unknown',
                'content': '',
                'timestamp': None,
                'engagement_data': {},
                'scraped_at': datetime.now().isoformat()
            }
    
    async def _extract_engagement_metrics(self) -> Dict[str, Any]:
        """Extract engagement metrics from the post."""
        try:
            # Look for engagement buttons and their counts
            engagement_selectors = {
                'likes': '[data-testid="like"]',
                'retweets': '[data-testid="retweet"]',
                'replies': '[data-testid="reply"]',
                'bookmarks': '[data-testid="bookmark"]'
            }
            
            engagement_data = {}
            
            for metric, selector in engagement_selectors.items():
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        # Try to get the count from aria-label or text content
                        aria_label = await element.get_attribute('aria-label')
                        if aria_label:
                            # Extract number from aria-label (e.g., "1,234 likes")
                            import re
                            numbers = re.findall(r'[\d,]+', aria_label)
                            if numbers:
                                engagement_data[metric] = numbers[0].replace(',', '')
                            else:
                                engagement_data[metric] = '0'
                        else:
                            engagement_data[metric] = '0'
                    else:
                        engagement_data[metric] = '0'
                except:
                    engagement_data[metric] = '0'
            
            return engagement_data
            
        except Exception as e:
            print(f"Error extracting engagement metrics: {str(e)}")
            return {}
    
    async def scrape_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a user's profile for engagement statistics.
        
        Args:
            username: X username to scrape
            
        Returns:
            Dictionary containing user profile data
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            profile_url = f"https://x.com/{username}"
            await self.page.goto(profile_url, wait_until='networkidle', timeout=30000)
            
            # Wait for profile to load
            await self.page.wait_for_selector('[data-testid="UserName"]', timeout=10000)
            
            # Extract profile information
            profile_data = await self._extract_profile_data()
            profile_data['username'] = username
            profile_data['url'] = profile_url
            
            return profile_data
            
        except Exception as e:
            print(f"Error scraping profile {username}: {str(e)}")
            return None
    
    async def _extract_profile_data(self) -> Dict[str, Any]:
        """Extract profile data from the page."""
        try:
            # Extract follower/following counts
            stats_elements = await self.page.query_selector_all('[data-testid="UserProfileHeader_Items"] a')
            
            stats = {}
            for element in stats_elements:
                text = await element.inner_text()
                if 'Following' in text:
                    stats['following'] = text.split()[0]
                elif 'Followers' in text:
                    stats['followers'] = text.split()[0]
            
            # Extract bio
            bio_element = await self.page.query_selector('[data-testid="UserDescription"]')
            bio = await bio_element.inner_text() if bio_element else ""
            
            return {
                'bio': bio.strip(),
                'stats': stats,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error extracting profile data: {str(e)}")
            return {'bio': '', 'stats': {}, 'scraped_at': datetime.now().isoformat()}
    
    async def close(self):
        """Close the browser and cleanup resources."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        self.is_initialized = False
    
    async def __aenter__(self):
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

