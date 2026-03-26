# 🧠 HackerNews Intelligence MCP

<p align="center">
  <a href="https://github.com/SJ2006-stack/hn-intelligence-mcp/stargazers">
    <img src="https://img.shields.io/github/stars/SJ2006-stack/hn-intelligence-mcp?style=for-the-badge&color=fac360&logo=github" alt="GitHub stars" />
  </a>
  
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  </a>

  <a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/badge/built%20with-uv-DA2198?style=for-the-badge&logo=python" alt="Built with uv" />
  </a>

  <a href="https://github.com/SJ2006-stack/hn-intelligence-mcp/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/SJ2006-stack/hn-intelligence-mcp?style=for-the-badge" alt="License: MIT" />
  </a>
</p>

A Model Context Protocol (MCP) server that extracts real signal from Hacker News ,not summaries, not trends, not vibes. Actual anomalies.

- **Pure Python Data Science Stack:** Built with Python to easily integrate tools like VADER NLP and robust data-wrangling libraries, which are vastly superior to JS for text analysis.

## ⚠️ The Problem

Every "HackerNews summary" tool does the exact same thing: dump 5,000 raw comments into an LLM and ask "what's trending?" The result is slow, expensive, and hallucinates generic tech trends.

**This is different.**

Signal extraction happens before your AI sees any data. The LLM receives a hyper-dense payload of pre-computed anomalies, not raw noise.

## ⚙️ How It Works

Four filters run locally, distilling the noise into pure signal:

| Filter | What it detects | How |
|---|---|---|
| Controversy | High friction topics | `comments >> upvotes` ratio |
| Deep Arguments | Technical debates | Comment length > 1000 chars |
| Sentiment Extremes | Emotional outliers | VADER NLP, compound > 0.7 |
| Resurrection | Old ideas resurfacing | Vintage year tags + URL diff |

Your AI only sees the output of these filters — typically 10-20 highly relevant items instead of 5,000 sprawling comments. Fast. Cheap. Actually intelligent.

## 🚀 Quickstart (Zero Install or Local Server)

You can use this server in two ways: connect it to your AI environment or run it locally as a standalone server.

### Option 1: Connect with AI Tools

#### Claude Desktop
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
        "from",
        "git+https://github.com/SJ2006-stack/hn-intelligence-mcp.git",
        "hn-intelligence-mcp"
      ]
    }
  }
}
```

Restart Claude Desktop.

#### VS Code / Cursor (via Cline, Roo, or similar)
Open your extension's MCP settings (e.g., `Cmd/Ctrl + Shift + P` → `Cline: Open MCP Settings`).

Paste the following configuration:

```json
{
  "mcpServers": {
    "hn-intelligence": {
      "command": "uvx",
      "args": [
        "from",
        "git+https://github.com/SJ2006-stack/hn-intelligence-mcp.git",
        "hn-intelligence-mcp"
      ]
    }
  }
}
```

> Note: If your code editor struggles to find `uvx` on macOS, change `"command"` to the absolute path, for example: `"/opt/homebrew/bin/uvx"`.

### Option 2: Run as a Local Server

To run the server locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/SJ2006-stack/hn-intelligence-mcp.git
   cd hn-intelligence-mcp
   ```
2. Set up a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Start the server:
   ```bash
   python server.py
   ```

The server will start and listen on `http://localhost:8000` (or another port if specified).

### Troubleshooting

- **Server not starting**: Ensure all dependencies are installed (`pip install -r requirements.txt`).
- **Command not found**: If `uvx` is not found, provide the absolute path to the binary.
- **Port conflicts**: If the default port is in use, specify a different port when starting the server.

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
git clone https://github.com/SJ2006-stack/hn-intelligence-mcp.git
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

## 🤝 Contributing & Support

If this saved your context window from being flooded with HN noise, please consider giving it a ⭐️. Pull requests for new signal filters are always welcome!

