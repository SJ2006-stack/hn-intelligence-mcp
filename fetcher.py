import requests
import functools
import time
import re
from urllib.parse import urlparse, parse_qs

ALGOLIA_URL = "https://hn.algolia.com/api/v1"
FIREBASE_URL = "https://hacker-news.firebaseio.com/v0"

def get_timestamp_bucket():
    # Buckets time into 30-min windows
    # Forces cache refresh every 30 minutes
    return int(time.time() / 1800)


def _get_json(url: str, params: dict | None = None):
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def _hn_url(item_id: str | int) -> str:
    return f"https://news.ycombinator.com/item?id={item_id}"


def _normalize_algolia_story(hit: dict) -> dict:
    item_id = hit.get("objectID") or hit.get("story_id")
    return {
        "id": int(item_id) if item_id else None,
        "title": hit.get("title", ""),
        "url": hit.get("url", ""),
        "author": hit.get("author", ""),
        "points": hit.get("points", 0),
        "num_comments": hit.get("num_comments", 0),
        "created_at": hit.get("created_at"),
        "created_at_i": hit.get("created_at_i"),
        "hn_url": _hn_url(item_id) if item_id else ""
    }


def _normalize_firebase_story(item: dict) -> dict:
    item_id = item.get("id")
    return {
        "id": item_id,
        "title": item.get("title", ""),
        "url": item.get("url", ""),
        "author": item.get("by", ""),
        "points": item.get("score", 0),
        "num_comments": item.get("descendants", 0),
        "created_at_i": item.get("time"),
        "hn_url": _hn_url(item_id) if item_id else ""
    }


def _coerce_domain(domain_or_url: str) -> str:
    raw = domain_or_url.strip().lower()
    if not raw:
        return ""
    if raw.startswith("http://") or raw.startswith("https://"):
        parsed = urlparse(raw)
        host = parsed.netloc
    else:
        host = raw.split("/")[0]
    return host.removeprefix("www.")


def _resolve_post_id(post_url_or_id: str | int) -> int:
    if isinstance(post_url_or_id, int):
        return post_url_or_id

    raw = str(post_url_or_id).strip()
    if raw.isdigit():
        return int(raw)

    # Hacker News item URL support, e.g. https://news.ycombinator.com/item?id=123
    parsed = urlparse(raw)
    if parsed.netloc.endswith("ycombinator.com"):
        query_id = parse_qs(parsed.query).get("id")
        if query_id and query_id[0].isdigit():
            return int(query_id[0])

    # Support direct Firebase-style item path fragments
    id_match = re.search(r"item/(\d+)", raw)
    if id_match:
        return int(id_match.group(1))

    # External URL: try to resolve through Algolia URL search.
    payload = _get_json(
        f"{ALGOLIA_URL}/search",
        params={
            "query": raw,
            "tags": "story",
            "restrictSearchableAttributes": "url",
            "hitsPerPage": 1
        }
    )
    hits = payload.get("hits", [])
    if hits:
        hit_id = hits[0].get("objectID")
        if hit_id and str(hit_id).isdigit():
            return int(hit_id)

    raise ValueError("Could not resolve a Hacker News item id from the provided input.")


def _fetch_firebase_item(item_id: int):
    return _get_json(f"{FIREBASE_URL}/item/{item_id}.json")

@functools.lru_cache(maxsize=128)
def search_stories(query: str, timestamp: int):
    """
    Fetch top 100 stories for a query.
    Cached per 30-min window to prevent Claude reasoning loops.
    Each user hits Algolia from their own IP — no global throttle risk.
    """
    response = requests.get(
        f"{ALGOLIA_URL}/search",
        params={
            "query": query,
            "tags": "story",
            "hitsPerPage": 100
        },
        timeout=20
    )
    response.raise_for_status()
    return response.json()["hits"]

@functools.lru_cache(maxsize=128)
def search_comments(query: str, timestamp: int):
    """
    Fetch top 500 comments for a query.
    Cached per 30-min window to prevent Claude reasoning loops.
    """
    response = requests.get(
        f"{ALGOLIA_URL}/search",
        params={
            "query": query,
            "tags": "comment",
            "hitsPerPage": 500
        },
        timeout=20
    )
    response.raise_for_status()
    return response.json()["hits"]


@functools.lru_cache(maxsize=128)
def get_recent_posts_data(timestamp: int, lookback_hours: int = 24, limit: int = 30):
    since = int(time.time()) - (lookback_hours * 3600)
    payload = _get_json(
        f"{ALGOLIA_URL}/search_by_date",
        params={
            "tags": "story",
            "numericFilters": f"created_at_i>{since}",
            "hitsPerPage": min(max(limit, 1), 100)
        }
    )
    hits = payload.get("hits", [])
    return [_normalize_algolia_story(hit) for hit in hits][:limit]


@functools.lru_cache(maxsize=128)
def get_top_posts_data(timestamp: int, lookback_hours: int = 24, limit: int = 30):
    since = int(time.time()) - (lookback_hours * 3600)
    payload = _get_json(
        f"{ALGOLIA_URL}/search",
        params={
            "tags": "story",
            "numericFilters": f"created_at_i>{since}",
            "hitsPerPage": 100
        }
    )
    hits = payload.get("hits", [])
    normalized = [_normalize_algolia_story(hit) for hit in hits]
    normalized.sort(key=lambda x: x.get("points", 0), reverse=True)
    return normalized[:limit]


@functools.lru_cache(maxsize=128)
def search_by_author_data(author: str, timestamp: int, limit: int = 30):
    author = author.strip()
    if not author:
        return []

    payload = _get_json(
        f"{ALGOLIA_URL}/search",
        params={
            "tags": f"story,author_{author}",
            "hitsPerPage": min(max(limit, 1), 100)
        }
    )
    hits = payload.get("hits", [])
    return [_normalize_algolia_story(hit) for hit in hits][:limit]


@functools.lru_cache(maxsize=128)
def search_by_domain_data(domain: str, timestamp: int, limit: int = 30):
    target_domain = _coerce_domain(domain)
    if not target_domain:
        return []

    payload = _get_json(
        f"{ALGOLIA_URL}/search",
        params={
            "query": f"site:{target_domain}",
            "tags": "story",
            "hitsPerPage": 100
        }
    )

    filtered = []
    for hit in payload.get("hits", []):
        story_url = hit.get("url") or ""
        host = _coerce_domain(story_url)
        if host == target_domain or host.endswith(f".{target_domain}"):
            filtered.append(_normalize_algolia_story(hit))

    return filtered[:limit]


def get_post_comments_data(
    post_url_or_id: str,
    max_depth: int = 8,  # Ignored in new implementation
    max_comments: int = 200,
):
    """
    Fetch all comments for a post using a single Algolia API call.
    Returns a flat list of comments (no tree structure).
    """
    post_id = _resolve_post_id(post_url_or_id)
    # Fetch post metadata from Firebase for consistency
    post = _fetch_firebase_item(post_id)
    if not post:
        raise ValueError("Post not found.")

    payload = _get_json(
        f"{ALGOLIA_URL}/search",
        params={
            "tags": f"comment,story_{post_id}",
            "hitsPerPage": max_comments
        }
    )
    comments = payload.get("hits", [])

    return {
        "post": _normalize_firebase_story(post),
        "comments": comments,
        "total_comments_returned": len(comments),
        "truncated": len(comments) >= max_comments
    }