"""
Engagement calculation and comparison logic for X (Twitter) posts.
Handles engagement scoring, trend analysis, and comparative metrics.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics
import math

def compute_comparison(results: list):
    """
    Compute comparison between multiple handle results.
    
    Args:
        results: List of engagement data for different handles
        
    Returns:
        Dictionary containing comparison analysis
    """
    if not results:
        return {"error": "No results to compare"}
    
    # Calculate total engagement for each handle
    handle_scores = {}
    for result in results:
        handle = result.get('handle', 'unknown')
        total_engagement = result.get('total_engagement', 0)
        handle_scores[handle] = total_engagement
    
    # Find the best performing handle
    best_handle = max(handle_scores.items(), key=lambda x: x[1])
    
    # Calculate average engagement
    avg_engagement = sum(handle_scores.values()) / len(handle_scores)
    
    return {
        'best_performing_handle': best_handle[0],
        'best_score': best_handle[1],
        'average_engagement': avg_engagement,
        'handle_rankings': sorted(handle_scores.items(), key=lambda x: x[1], reverse=True),
        'total_handles_compared': len(results)
    }

class EngagementCalculator:
    """Calculator for X engagement metrics and comparisons."""
    
    def __init__(self):
        """Initialize the engagement calculator."""
        self.engagement_history = []
        self.user_stats = {}
    
    def analyze_engagement(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze engagement metrics and calculate scores.
        
        Args:
            metrics: Dictionary containing engagement metrics
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Parse numeric values from metrics
            parsed_metrics = self._parse_engagement_metrics(metrics)
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(parsed_metrics)
            
            # Calculate additional metrics
            virality_score = self._calculate_virality_score(parsed_metrics)
            interaction_rate = self._calculate_interaction_rate(parsed_metrics)
            
            # Determine engagement tier
            engagement_tier = self._determine_engagement_tier(engagement_score)
            
            # Generate insights
            insights = self._generate_insights(parsed_metrics, engagement_score)
            
            return {
                'engagement_score': engagement_score,
                'virality_score': virality_score,
                'interaction_rate': interaction_rate,
                'engagement_tier': engagement_tier,
                'parsed_metrics': parsed_metrics,
                'insights': insights,
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f'Failed to analyze engagement: {str(e)}',
                'engagement_score': 0,
                'calculated_at': datetime.now().isoformat()
            }
    
    def _parse_engagement_metrics(self, metrics: Dict[str, Any]) -> Dict[str, int]:
        """Parse engagement metrics and convert to integers."""
        parsed = {}
        
        # Define metric mappings
        metric_fields = ['likes', 'retweets', 'replies', 'bookmarks', 'views']
        
        for field in metric_fields:
            value = metrics.get(field, 'N/A')
            if value == 'N/A' or not value:
                parsed[field] = 0
            else:
                parsed[field] = self._parse_numeric_value(str(value))
        
        return parsed
    
    def _parse_numeric_value(self, value: str) -> int:
        """Parse numeric values with K, M, B suffixes."""
        if not value or value == 'N/A':
            return 0
        
        value = value.strip().upper()
        
        # Remove commas
        value = value.replace(',', '')
        
        # Handle suffixes
        if value.endswith('K'):
            return int(float(value[:-1]) * 1000)
        elif value.endswith('M'):
            return int(float(value[:-1]) * 1000000)
        elif value.endswith('B'):
            return int(float(value[:-1]) * 1000000000)
        else:
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return 0
    
    def _calculate_engagement_score(self, metrics: Dict[str, int]) -> float:
        """
        Calculate weighted engagement score.
        
        Formula: (likes * 1) + (retweets * 3) + (replies * 2) + (bookmarks * 0.5) + (views * 0.01)
        """
        likes = metrics.get('likes', 0)
        retweets = metrics.get('retweets', 0)
        replies = metrics.get('replies', 0)
        bookmarks = metrics.get('bookmarks', 0)
        views = metrics.get('views', 0)
        
        # Weighted calculation
        score = (
            likes * 1.0 +
            retweets * 3.0 +
            replies * 2.0 +
            bookmarks * 0.5 +
            views * 0.01
        )
        
        # Normalize to 0-100 scale
        normalized_score = min(score / 1000, 100)
        
        return round(normalized_score, 2)
    
    def _calculate_virality_score(self, metrics: Dict[str, int]) -> float:
        """Calculate virality score based on retweets and views ratio."""
        retweets = metrics.get('retweets', 0)
        views = metrics.get('views', 0)
        
        if views == 0:
            return 0.0
        
        # Virality = (retweets / views) * 100
        virality = (retweets / views) * 100
        return round(min(virality, 100), 2)
    
    def _calculate_interaction_rate(self, metrics: Dict[str, int]) -> float:
        """Calculate interaction rate (likes + retweets + replies) / views."""
        likes = metrics.get('likes', 0)
        retweets = metrics.get('retweets', 0)
        replies = metrics.get('replies', 0)
        views = metrics.get('views', 0)
        
        if views == 0:
            return 0.0
        
        interactions = likes + retweets + replies
        rate = (interactions / views) * 100
        
        return round(min(rate, 100), 2)
    
    def _determine_engagement_tier(self, score: float) -> str:
        """Determine engagement tier based on score."""
        if score >= 80:
            return "Viral"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def _generate_insights(self, metrics: Dict[str, int], score: float) -> List[str]:
        """Generate insights based on engagement metrics."""
        insights = []
        
        likes = metrics.get('likes', 0)
        retweets = metrics.get('retweets', 0)
        replies = metrics.get('replies', 0)
        views = metrics.get('views', 0)
        
        # Engagement insights
        if score >= 80:
            insights.append("🔥 This post is performing exceptionally well!")
        elif score >= 60:
            insights.append("📈 Strong engagement - this content resonates with your audience")
        elif score >= 40:
            insights.append("👍 Good engagement - room for improvement")
        elif score >= 20:
            insights.append("📊 Moderate engagement - consider optimizing content")
        else:
            insights.append("💡 Low engagement - try different content strategies")
        
        # Specific metric insights
        if retweets > likes * 0.5:
            insights.append("🔄 High retweet rate indicates shareable content")
        
        if replies > likes * 0.3:
            insights.append("💬 High reply rate shows strong audience engagement")
        
        if views > 0 and (likes + retweets + replies) / views < 0.05:
            insights.append("👀 High view count but low interaction - consider more engaging content")
        
        return insights
    
    async def get_user_comparison(self, username: str) -> Dict[str, Any]:
        """
        Get comparison data for a specific user.
        
        Args:
            username: X username to get comparison data for
            
        Returns:
            Dictionary containing user comparison metrics
        """
        try:
            # This would typically fetch from a database or API
            # For now, return mock data structure
            return {
                'username': username,
                'average_engagement_score': 45.2,
                'best_performing_post_score': 78.9,
                'engagement_trend': 'increasing',
                'total_posts_analyzed': 25,
                'comparison_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': f'Failed to get user comparison: {str(e)}'}
    
    async def get_user_stats(self, username: str) -> Dict[str, Any]:
        """
        Get comprehensive user statistics.
        
        Args:
            username: X username to analyze
            
        Returns:
            Dictionary containing user statistics
        """
        try:
            # Mock user stats - in production, this would query a database
            return {
                'username': username,
                'total_posts': 150,
                'average_engagement_score': 42.5,
                'engagement_trend': 'stable',
                'best_performing_content_types': ['threads', 'polls', 'images'],
                'peak_posting_times': ['9:00 AM', '1:00 PM', '7:00 PM'],
                'follower_growth_rate': 2.3,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': f'Failed to get user stats: {str(e)}'}
    
    async def get_trending_analysis(self) -> Dict[str, Any]:
        """
        Get trending engagement analysis.
        
        Returns:
            Dictionary containing trending analysis
        """
        try:
            # Mock trending data - in production, this would analyze real data
            return {
                'trending_topics': [
                    {'topic': 'AI', 'engagement_score': 85.2, 'post_count': 1250},
                    {'topic': 'Climate', 'engagement_score': 78.9, 'post_count': 980},
                    {'topic': 'Tech', 'engagement_score': 72.1, 'post_count': 2100}
                ],
                'average_engagement_today': 45.8,
                'engagement_trend': 'increasing',
                'most_engaging_content_types': ['videos', 'threads', 'polls'],
                'analysis_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': f'Failed to get trending analysis: {str(e)}'}
    
    def compare_posts(self, post1_metrics: Dict[str, Any], post2_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two posts' engagement metrics.
        
        Args:
            post1_metrics: First post engagement metrics
            post2_metrics: Second post engagement metrics
            
        Returns:
            Dictionary containing comparison results
        """
        try:
            analysis1 = self.analyze_engagement(post1_metrics)
            analysis2 = self.analyze_engagement(post2_metrics)
            
            score1 = analysis1.get('engagement_score', 0)
            score2 = analysis2.get('engagement_score', 0)
            
            return {
                'post1_score': score1,
                'post2_score': score2,
                'score_difference': round(score1 - score2, 2),
                'better_performing_post': 'post1' if score1 > score2 else 'post2',
                'performance_ratio': round(score1 / score2, 2) if score2 > 0 else float('inf'),
                'comparison_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': f'Failed to compare posts: {str(e)}'}
    
    def calculate_engagement_velocity(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate engagement velocity over time.
        
        Args:
            metrics_history: List of engagement metrics over time
            
        Returns:
            Dictionary containing velocity analysis
        """
        try:
            if len(metrics_history) < 2:
                return {'error': 'Need at least 2 data points for velocity calculation'}
            
            scores = []
            timestamps = []
            
            for metrics in metrics_history:
                analysis = self.analyze_engagement(metrics)
                scores.append(analysis.get('engagement_score', 0))
                timestamps.append(datetime.fromisoformat(metrics.get('parsed_at', datetime.now().isoformat())))
            
            # Calculate velocity (change in score over time)
            velocity_data = []
            for i in range(1, len(scores)):
                time_diff = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # hours
                score_diff = scores[i] - scores[i-1]
                velocity = score_diff / time_diff if time_diff > 0 else 0
                velocity_data.append(velocity)
            
            avg_velocity = statistics.mean(velocity_data) if velocity_data else 0
            velocity_trend = 'increasing' if avg_velocity > 0 else 'decreasing' if avg_velocity < 0 else 'stable'
            
            return {
                'average_velocity': round(avg_velocity, 2),
                'velocity_trend': velocity_trend,
                'data_points': len(metrics_history),
                'velocity_calculation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Failed to calculate velocity: {str(e)}'}

