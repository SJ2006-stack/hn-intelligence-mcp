# 🧠 HN Intelligence MCP

A Model Context Protocol (MCP) server that extracts real signal from Hacker News — not summaries, not trends, not vibes. Actual anomalies.

## ⚠️ The Problem

Every "HN summary" tool does the exact same thing: dump 5,000 raw comments into an LLM and ask "what's trending?" The result is slow, expensive, and hallucinates generic tech trends.

**This is different.**

Signal extraction happens before your AI sees any data. The LLM receives a hyper-dense payload of pre-computed anomalies — not raw noise.

## ⚙️ How It Works

Four filters run locally, distilling the noise into pure signal:

| Filter | What it detects | How |
|---|---|---|
| Controversy | High friction topics | `comments >> upvotes` ratio |
| Deep Arguments | Technical debates | Comment length > 1000 chars |
| Sentiment Extremes | Emotional outliers | VADER NLP, compound > 0.7 |
| Resurrection | Old ideas resurfacing | Vintage year tags + URL diff |

Your AI only sees the output of these filters — typically 10-20 highly relevant items instead of 5,000 sprawling comments. Fast. Cheap. Actually intelligent.

## 🚀 Quickstart (Zero Install)

You do not need to clone this repository to use it. If you have `uv` installed, you can run this server instantly in your favorite AI environment.

### Option 1: Claude Desktop

Open your Claude Desktop configuration file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following to your `mcpServers` object:

```json
{
  "mcpServers": {
    "hn-intelligence": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yourusername/hn-intelligence-mcp.git",
        "hn-intelligence-mcp"
      ]
    }
  }
}
```

Restart Claude Desktop.

### Option 2: VS Code / Cursor (via Cline, Roo, or similar)

Open your extension's MCP settings (e.g., `Cmd/Ctrl + Shift + P` → `Cline: Open MCP Settings`).

Paste the following configuration:

```json
{
  "mcpServers": {
    "hn-intelligence": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yourusername/hn-intelligence-mcp.git",
        "hn-intelligence-mcp"
      ]
    }
  }
}
```

> Note: If your code editor struggles to find `uvx` on macOS, change `"command"` to the absolute path, for example: `"/opt/homebrew/bin/uvx"`.

## 🛠️ Usage Examples

Once connected, ask your AI anything about the current state of Hacker News:

- "What's the real developer sentiment around Next.js right now?"
- "What technical friction are people experiencing with Supabase?"
- "What old ideas about databases are suddenly relevant again?"
- "Where is developer thinking actually moving on AI coding tools?"

## 🧰 Available Tools

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

## 🏗️ Architecture & Why This Is Different

- No API key needed — Algolia HN API is free and public.
- No global throttling — MCP runs locally, each user hits Algolia from their own IP.
- No hallucinations — Your AI reasons over mathematical signals, not raw data.
- No context window waste — 200 tokens of signal vs 50,000 tokens of noise.
- 30-minute cache — Prevents LLM reasoning loops and returns instantly on repeat calls.

```text
Algolia HN API
      ↓
  fetcher.py        ← Raw data, cached per 30-min window
      ↓
  filters.py        ← 4 signal extractors, pure Python, no LLM
      ↓
  server.py         ← FastMCP tools, hyper-dense JSON payload
      ↓
   Your AI          ← Reasons over signal only
```

### Data Sources

- `https://hn.algolia.com/api/v1` for date-based search, author/domain filtering, and score sorting.
- `https://hacker-news.firebaseio.com/v0` for top/new/best feeds and recursive comment retrieval.

## 💻 Local Development

If you want to modify the filters or add new tools, clone the repository and run it locally:

```bash
git clone https://github.com/yourusername/hn-intelligence-mcp.git
cd hn-intelligence-mcp
```

Configure your MCP client to point to your local directory:

```json
{
  "mcpServers": {
    "hn-intelligence": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/hn-intelligence-mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

## License

MIT