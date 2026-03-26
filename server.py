from mcp.server.fastmcp import FastMCP
from fetcher import (
    search_stories,
    search_comments,
    get_timestamp_bucket,
    get_recent_posts_data,
    get_top_posts_data,
    search_by_author_data,
    search_by_domain_data,
    get_post_comments_data
)
from filters import (
    controversy_filter,
    deep_tree_filter,
    sentiment_filter,
    resurrection_filter
)
import json

mcp = FastMCP("HN-Intelligence")


@mcp.tool()
def analyze_topic(topic: str) -> str:
    """
    Analyzes Hacker News for real signal about any topic.
    
    Returns pre-processed anomalies only — not raw data.
    Uses 4 filters: Controversy, Deep Arguments, Sentiment Extremes, Resurrection.
    Claude receives a hyper-dense signal payload instead of 5000 raw comments.
    Fast, cheap, and genuinely intelligent.
    """
    bucket = get_timestamp_bucket()

    stories = search_stories(topic, bucket)
    comments = search_comments(topic, bucket)

    controversial = controversy_filter(stories)
    deep = deep_tree_filter(comments)
    sentiment = sentiment_filter(comments)
    resurrected = resurrection_filter(stories)

    payload = {
        "topic": topic,
        "total_stories_analyzed": len(stories),
        "total_comments_analyzed": len(comments),
        "signals": {
            "controversy": {
                "description": "Posts where comments >> upvotes. High friction topics.",
                "count": len(controversial),
                "data": controversial
            },
            "deep_arguments": {
                "description": "Longest, most detailed technical comments. High-effort debate.",
                "count": len(deep),
                "data": deep
            },
            "sentiment_extremes": {
                "description": "Statistically extreme emotional reactions. Compound score > 0.7",
                "data": sentiment
            },
            "resurrection": {
                "description": "Old ideas suddenly relevant again. Vintage tags or URL resubmissions.",
                "count": len(resurrected),
                "data": resurrected
            }
        },
        "instruction": (
            f"These are pre-filtered anomalies about '{topic}' from Hacker News. "
            f"Do not generalize. Do not invent trends. "
            f"Analyze ONLY what these specific signals tell you about where "
            f"developer thinking is actually moving right now."
        )
    }

    return json.dumps(payload, indent=2)


@mcp.tool()
def get_controversial_posts(topic: str) -> str:
    """
    Get only the most controversial HN posts about a topic.
    Controversy = comment count far exceeds upvote count.
    """
    bucket = get_timestamp_bucket()
    stories = search_stories(topic, bucket)
    result = controversy_filter(stories)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_deep_arguments(topic: str) -> str:
    """
    Get the longest, most detailed technical comments about a topic.
    Proxy for high-effort technical debate and deep disagreement.
    """
    bucket = get_timestamp_bucket()
    comments = search_comments(topic, bucket)
    result = deep_tree_filter(comments)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_sentiment_extremes(topic: str) -> str:
    """
    Get the most emotionally charged HN comments about a topic.
    Filters out neutral noise. Returns only statistical outliers.
    """
    bucket = get_timestamp_bucket()
    comments = search_comments(topic, bucket)
    result = sentiment_filter(comments)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_resurrected_topics(topic: str) -> str:
    """
    Find old ideas about a topic suddenly getting attention again.
    Detects vintage HN articles resurfacing and URL resubmission explosions.
    """
    bucket = get_timestamp_bucket()
    stories = search_stories(topic, bucket)
    result = resurrection_filter(stories)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_recent_posts(hours: int = 24, limit: int = 30) -> str:
    """
    Browse recent Hacker News stories from the last N hours.
    Uses Algolia's search_by_date feed and returns latest posts first.
    """
    bucket = get_timestamp_bucket()
    safe_hours = max(1, min(hours, 24 * 30))
    safe_limit = max(1, min(limit, 100))
    result = get_recent_posts_data(bucket, lookback_hours=safe_hours, limit=safe_limit)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_top_posts(hours: int = 24, limit: int = 30) -> str:
    """
    Get top Hacker News stories by upvotes in the last N hours.
    """
    bucket = get_timestamp_bucket()
    safe_hours = max(1, min(hours, 24 * 30))
    safe_limit = max(1, min(limit, 100))
    result = get_top_posts_data(bucket, lookback_hours=safe_hours, limit=safe_limit)
    return json.dumps(result, indent=2)


@mcp.tool()
def search_by_author(author: str, limit: int = 30) -> str:
    """
    Search Hacker News stories by author username.
    """
    bucket = get_timestamp_bucket()
    safe_limit = max(1, min(limit, 100))
    result = search_by_author_data(author, bucket, limit=safe_limit)
    return json.dumps(result, indent=2)


@mcp.tool()
def search_by_domain(domain: str, limit: int = 30) -> str:
    """
    Search Hacker News stories for a domain (e.g. example.com).
    """
    bucket = get_timestamp_bucket()
    safe_limit = max(1, min(limit, 100))
    result = search_by_domain_data(domain, bucket, limit=safe_limit)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_post_comments(post_url_or_id: str, max_depth: int = 8, max_comments: int = 200) -> str:
    """
    Get threaded comments for a specific Hacker News post by item ID or URL.
    Supports HN item URLs and external article URLs.
    """
    safe_depth = max(1, min(max_depth, 20))
    safe_comments = max(1, min(max_comments, 1000))
    result = get_post_comments_data(
        post_url_or_id=post_url_or_id,
        max_depth=safe_depth,
        max_comments=safe_comments,
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def get_trending(feed: str = "top", limit: int = 30) -> str:
    """
    Track live trending stories from Hacker News feeds without keyword filtering.
    feed: top | new | best
    """
    bucket = get_timestamp_bucket()
    safe_limit = max(1, min(limit, 100))
    result = get_trending_data(bucket, feed=feed, limit=safe_limit)
    return json.dumps(result, indent=2)


def get_trending_data(bucket: str, feed: str, limit: int) -> dict:
    """
    Fetch trending stories from Hacker News based on the feed type and limit.
    This is a placeholder implementation and should be replaced with actual logic.

    Args:
        bucket (str): Timestamp bucket for caching or grouping data.
        feed (str): The feed type (e.g., 'top', 'new', 'best').
        limit (int): The maximum number of stories to fetch.

    Returns:
        dict: A dictionary containing mock trending data.
    """
    # Placeholder data to simulate functionality
    return {
        "bucket": bucket,
        "feed": feed,
        "stories": [
            {"id": i, "title": f"Story {i}", "url": f"https://example.com/story{i}"}
            for i in range(1, limit + 1)
        ],
    }


if __name__ == "__main__":
    mcp.run()