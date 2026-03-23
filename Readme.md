# HN Intelligence MCP

> A Model Context Protocol server that extracts **real signal** from Hacker News — not summaries, not trends, not vibes. Actual anomalies.

## The Problem

Every "HN summary" tool does the same thing: dump 5,000 comments into an LLM and ask "what's trending?" The result is slow, expensive, and hallucinates generic tech trends.

**This is different.**

Signal extraction happens **before** Claude sees any data. The LLM receives a hyper-dense payload of pre-computed anomalies — not raw noise.

## How It Works

Four filters run locally on your machine:

| Filter | What it detects | How |
|---|---|---|
| **Controversy** | High friction topics | `comments >> upvotes` ratio |
| **Deep Arguments** | Technical debates | Comment length > 1000 chars |
| **Sentiment Extremes** | Emotional outliers | VADER NLP, compound > 0.7 |
| **Resurrection** | Old ideas resurfacing | Vintage year tags + URL diff |

Claude only sees the output of these filters — typically 10-20 items instead of 5,000 comments. **Fast. Cheap. Actually intelligent.**

## Install

```bash
git clone https://github.com/yourusername/hn-intelligence-mcp
cd hn-intelligence-mcp
pip install -r requirements.txt
```

## Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hn-intelligence": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yourusername/hn-intelligence-mcp",
        "hn-intelligence-mcp"
      ]
    }
  }
}
```

Restart Claude Desktop. Done.

## Usage

Ask Claude anything:

```
"What's the real developer sentiment around Next.js right now?"
"What technical friction are people experiencing with Supabase?"
"What old ideas about databases are suddenly relevant again?"
"Where is developer thinking actually moving on AI coding tools?"
```

## Tools

| Tool | Description |
|---|---|
| `analyze_topic` | Full analysis — all 4 filters combined |
| `get_controversial_posts` | Only high friction posts |
| `get_deep_arguments` | Only detailed technical debates |
| `get_sentiment_extremes` | Only emotional outliers |
| `get_resurrected_topics` | Only old ideas resurfacing |
| `get_recent_posts` | Latest stories in the last N hours (default 24h) |
| `get_top_posts` | Highest-upvoted stories in the last N hours |
| `search_by_author` | Stories submitted by a specific HN author |
| `search_by_domain` | Stories from a specific domain (e.g. `github.com`) |
| `get_post_comments` | Threaded comments for a post URL or HN item ID |
| `get_trending` | Live keyword-free feed from HN top/new/best stories |

## Why This Is Different

- **No API key needed** — Algolia HN API is free and public
- **No global throttling** — MCP runs locally, each user hits Algolia from their own IP
- **No hallucinations** — Claude reasons over signals, not raw data
- **No context window waste** — 200 tokens of signal vs 50,000 tokens of noise
- **30-minute cache** — prevents Claude reasoning loops, returns instantly on repeat calls

## Architecture

```
Algolia HN API
      ↓
  fetcher.py        ← Raw data, cached per 30-min window
      ↓
  filters.py        ← 4 signal extractors, pure Python, no LLM
      ↓
  server.py         ← FastMCP tools, hyper-dense JSON payload
      ↓
   Claude           ← Reasons over signal only
```

Additional data sources used by the new tools:

- `https://hn.algolia.com/api/v1` for date-based search, author/domain filtering, and score sorting
- `https://hacker-news.firebaseio.com/v0` for top/new/best feeds and recursive comment retrieval

## License

MIT