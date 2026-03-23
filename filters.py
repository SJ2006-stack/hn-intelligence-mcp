import re
import nltk

# Fix 1: Download VADER lexicon on startup
# Runs silently, only downloads if not already present
nltk.download('vader_lexicon', quiet=True)

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


# Filter 1: Controversy (Ratio Filter)
# Logic: comments >> upvotes = high friction topic
def controversy_filter(stories: list) -> list:
    controversial = []
    for s in stories:
        score = s.get("points", 1) or 1
        comments = s.get("num_comments", 0)
        if comments > (score * 2) and comments > 50:
            controversial.append({
                "title": s["title"],
                "url": s.get("url", ""),
                "score": score,
                "comments": comments,
                "ratio": round(comments / score, 2),
                "hn_url": f"https://news.ycombinator.com/item?id={s['objectID']}"
            })
    return sorted(
        controversial,
        key=lambda x: x["ratio"],
        reverse=True
    )[:5]


# Filter 2: High-Effort Arguments (Patched)
# Fix 2: Algolia flat comment search does NOT return num_comments/children
# Use comment text length as proxy for effort and depth
# 1000+ chars on HN = detailed technical argument
def deep_tree_filter(comments: list) -> list:
    deep = []
    for c in comments:
        text = c.get("comment_text", "")
        if text and len(text) > 1000:
            deep.append({
                "text": text[:500] + "...",
                "full_length": len(text),
                "author": c.get("author", ""),
                "story_id": c.get("story_id", ""),
                "hn_url": f"https://news.ycombinator.com/item?id={c['objectID']}"
            })
    return sorted(
        deep,
        key=lambda x: x["full_length"],
        reverse=True
    )[:5]


# Filter 3: VADER Sentiment Extremes
# Discard neutral. Keep only the most emotionally charged comments.
def sentiment_filter(comments: list) -> dict:
    scored = []
    for c in comments:
        text = c.get("comment_text", "")
        if not text:
            continue
        score = analyzer.polarity_scores(text)
        # compound > 0.7 = strongly positive
        # compound < -0.7 = strongly negative
        if abs(score["compound"]) > 0.7:
            scored.append({
                "text": text[:300],
                "sentiment_score": round(score["compound"], 3),
                "sentiment": "positive" if score["compound"] > 0 else "negative",
                "author": c.get("author", ""),
                "hn_url": f"https://news.ycombinator.com/item?id={c['objectID']}"
            })
    scored.sort(key=lambda x: x["sentiment_score"])
    return {
        "most_negative": scored[:3],
        "most_positive": scored[-3:]
    }


# Filter 4: Resurrection (Patched)
# Fix 3: URL diff rarely works in 100-item batch
# Method A (vintage regex) is the workhorse — keep it primary
# Method B (URL diff) kept as nice-to-have bonus signal
def resurrection_filter(stories: list) -> list:
    resurrected = []

    # Method A: Vintage Tag (PRIMARY — most reliable)
    # HN mods append year to old articles on front page
    # e.g. "Why we left the Cloud (2020)"
    vintage_pattern = re.compile(r'\(20[12]\d\)')
    for s in stories:
        title = s.get("title", "")
        if vintage_pattern.search(title):
            comments = s.get("num_comments", 0)
            if comments > 30:
                resurrected.append({
                    "title": title,
                    "type": "vintage_resurface",
                    "signal": "Old article on front page today — industry re-evaluating past decision",
                    "comments": comments,
                    "hn_url": f"https://news.ycombinator.com/item?id={s['objectID']}"
                })

    # Method B: URL Diff (BONUS — triggers rarely but high signal when it does)
    # Same URL submitted twice with explosive comment growth
    url_map = {}
    for s in stories:
        url = s.get("url", "")
        if not url:
            continue
        if url in url_map:
            old = url_map[url]
            new_comments = s.get("num_comments", 0)
            old_comments = old.get("num_comments", 0)
            if new_comments > old_comments * 3 and new_comments > 20:
                resurrected.append({
                    "title": s["title"],
                    "type": "resubmission_explosion",
                    "signal": "Same URL — ignored before, exploding now",
                    "old_comments": old_comments,
                    "new_comments": new_comments,
                    "delta": new_comments - old_comments,
                    "url": url
                })
        else:
            url_map[url] = s

    return sorted(
        resurrected,
        key=lambda x: x.get("comments", x.get("delta", 0)),
        reverse=True
    )[:5]