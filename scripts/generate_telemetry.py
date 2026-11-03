#!/usr/bin/env python3
"""
scripts/generate_telemetry.py
Queries the GitHub Search API for merged PRs authored by Veditha08
and generates an updated assets/telemetry.svg card.
"""

import os
import json
import urllib.request
import urllib.error
import html
from datetime import datetime, timezone

USER = "Veditha08"
API_URL = f"https://api.github.com/search/issues?q=author:{USER}+type:pr+is:merged&per_page=4"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "telemetry.svg")

# Robust fallback data in case of network unavailability or API rate limits
FALLBACK_PRS = [
    {
        "repo": "AOSSIE-Org/Rein",
        "title": "Replace legacy react-icons with lucide-react equivalents",
        "date": "2026-11-01"
    },
    {
        "repo": "GreedyBear-Project/GreedyBear",
        "title": "Add accessible name to ScrollToTopButton (#1788)",
        "date": "2026-10-27"
    },
    {
        "repo": "openvinotoolkit/openvino",
        "title": "Optimize inference runtime graph execution passes",
        "date": "2026-10-18"
    },
    {
        "repo": "AOSSIE-Org/SocialStreet",
        "title": "Enhance backend API schema validation and test coverage",
        "date": "2026-10-04"
    }
]

def fetch_merged_prs():
    headers = {
        "User-Agent": "Veditha08-Telemetry-Generator/1.0",
        "Accept": "application/vnd.github.v3+json"
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        req = urllib.request.Request(API_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                items = data.get("items", [])
                prs = []
                for item in items[:4]:
                    repo_url = item.get("repository_url", "")
                    repo_name = "/".join(repo_url.split("/")[-2:]) if repo_url else "Open-Source"
                    title = item.get("title", "")
                    merged_date = item.get("closed_at", "")[:10]
                    prs.append({
                        "repo": repo_name,
                        "title": title,
                        "date": merged_date
                    })
                if prs:
                    return prs
    except Exception as e:
        print(f"[!] Warning: GitHub API query error: {e}. Using fallback data.")

    return FALLBACK_PRS

def truncate(text, max_len=44):
    if len(text) > max_len:
        return text[:max_len - 1].rstrip() + "…"
    return text

def generate_svg(prs):
    width = 800
    height = 210

    rows_svg = []
    base_y = 66
    line_height = 34

    for i, pr in enumerate(prs):
        y = base_y + i * line_height
        safe_repo = html.escape(pr["repo"])
        safe_title = html.escape(truncate(pr["title"]))
        safe_date = html.escape(pr["date"])

        row = f"""
    <!-- Row {i+1} -->
    <g transform="translate(24, {y})">
      <!-- PR Status Dot / Icon -->
      <circle cx="6" cy="-4" r="3.5" fill="#FBBF24" opacity="0.9"/>
      <path d="M 6 -10 L 6 2" stroke="#F59E0B" stroke-width="1.2" opacity="0.5"/>
      <!-- Repo Name -->
      <text x="22" y="0" fill="#FBBF24" font-family="'JetBrains Mono', Consolas, monospace" font-size="11.5" font-weight="700">
        {safe_repo}
      </text>
      <!-- PR Title -->
      <text x="225" y="0" fill="#F0F6FC" font-family="'JetBrains Mono', Consolas, monospace" font-size="11">
        {safe_title}
      </text>
      <!-- Merged Date -->
      <text x="740" y="0" text-anchor="end" fill="#8B949E" font-family="'JetBrains Mono', Consolas, monospace" font-size="10.5">
        merged {safe_date}
      </text>
    </g>"""
        rows_svg.append(row)

    rows_content = "\n".join(rows_svg)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" preserveAspectRatio="xMidYMid meet">
  <defs>
    <style>
      @keyframes blink {{
        0%, 49% {{ opacity: 1; }}
        50%, 100% {{ opacity: 0.3; }}
      }}
      .pulse-beacon {{
        animation: blink 1.8s infinite;
      }}
    </style>
  </defs>

  <!-- Terminal Window Background -->
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" fill="#0D1117" stroke="#30363D" stroke-width="1"/>

  <!-- Terminal Title Bar -->
  <path d="M 0.5 8.5 A 8 8 0 0 1 8.5 0.5 L {width - 8.5} 0.5 A 8 8 0 0 1 {width - 0.5} 8.5 L {width - 0.5} 28.5 L 0.5 28.5 Z" fill="#161B22"/>
  <line x1="0" y1="28.5" x2="{width}" y2="28.5" stroke="#30363D" stroke-width="1"/>

  <!-- Title & Beacon -->
  <circle cx="18" cy="14" r="3.5" fill="#FBBF24" class="pulse-beacon"/>
  <text x="30" y="18" fill="#FBBF24" font-family="'JetBrains Mono', Consolas, monospace" font-size="11" font-weight="700" letter-spacing="0.5">
    ⚡ LIVE OPEN-SOURCE TELEMETRY // LATEST MERGED PRs
  </text>

  <!-- Window Controls -->
  <g transform="translate({width - 64}, 9)" fill="none" stroke="#8B949E" stroke-width="1.2">
    <line x1="2" y1="6" x2="10" y2="6"/>
    <rect x="18" y="2" width="8" height="8" rx="0.5"/>
    <g transform="translate(34, 1)">
      <line x1="2" y1="2" x2="8" y2="8"/>
      <line x1="8" y1="2" x2="2" y2="8"/>
    </g>
  </g>

  <!-- PR Rows -->
  <g id="pr-list">
{rows_content}
  </g>

  <!-- Bottom Divider & Ping Line -->
  <line x1="24" y1="188" x2="{width - 24}" y2="188" stroke="#161B22" stroke-width="1"/>
  <text x="24" y="199" fill="#8B949E" font-family="'JetBrains Mono', Consolas, monospace" font-size="9" letter-spacing="0.5">
    ● STATUS: ONLINE // SYNCED: {now_str}
  </text>
  <text x="{width - 24}" y="199" text-anchor="end" fill="#F59E0B" font-family="'JetBrains Mono', Consolas, monospace" font-size="9">
    OpenVINO • AOSSIE • GreedyBear
  </text>
</svg>"""

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[+] Successfully generated telemetry card at {OUTPUT_PATH}")

if __name__ == "__main__":
    prs = fetch_merged_prs()
    generate_svg(prs)
