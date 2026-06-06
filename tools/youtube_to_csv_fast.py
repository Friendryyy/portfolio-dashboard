#!/usr/bin/env python3
"""
YouTube Search — fast, no API key required (uses YouTube Innertube API via requests)
Usage:
  python tools/youtube_to_csv_fast.py "NVDA stock analysis 2026" [--max 10] [--csv]
"""
import sys
import json
import argparse
import os
import requests
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_INNERTUBE_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_INNERTUBE_PAYLOAD_BASE = {
    "context": {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20240101.00.00",
            "hl": "en",
            "gl": "US",
        }
    }
}


def _extract_text(obj: dict, *keys) -> str:
    """Safely extract text from nested YouTube renderer objects."""
    for key in keys:
        runs = obj.get(key, {}).get("runs", [])
        if runs:
            return runs[0].get("text", "")
        simple = obj.get(key, {}).get("simpleText", "")
        if simple:
            return simple
    return ""


def search_youtube(query: str, max_results: int = 10) -> list[dict]:
    """Search YouTube using the Innertube API — no API key needed."""
    payload = {**_INNERTUBE_PAYLOAD_BASE, "query": query}

    try:
        resp = requests.post(
            "https://www.youtube.com/youtubei/v1/search",
            headers=_INNERTUBE_HEADERS,
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"HTTP error contacting YouTube: {e}")

    data = resp.json()

    # Navigate the nested structure to find video renderers
    sections = (
        data.get("contents", {})
        .get("twoColumnSearchResultsRenderer", {})
        .get("primaryContents", {})
        .get("sectionListRenderer", {})
        .get("contents", [])
    )

    videos = []
    for section in sections:
        items = section.get("itemSectionRenderer", {}).get("contents", [])
        for item in items:
            vr = item.get("videoRenderer", {})
            if not vr:
                continue

            video_id = vr.get("videoId", "")
            title = _extract_text(vr, "title")
            channel = _extract_text(vr, "ownerText", "longBylineText")
            published = _extract_text(vr, "publishedTimeText")
            views = _extract_text(vr, "viewCountText", "shortViewCountText")
            duration = _extract_text(vr, "lengthText")

            if video_id and title:
                videos.append({
                    "title": title,
                    "channel": channel,
                    "published": published,
                    "views": views,
                    "duration": duration,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                })

            if len(videos) >= max_results:
                return videos

    return videos


def main():
    parser = argparse.ArgumentParser(description="YouTube search — no API key required")
    parser.add_argument("query", help="Search query, e.g. 'NVDA stock analysis 2026'")
    parser.add_argument("--max", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--csv", action="store_true", help="Also save results to output/ as CSV")
    args = parser.parse_args()

    try:
        videos = search_youtube(args.query, args.max)
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    output = {"query": args.query, "count": len(videos), "videos": videos}
    print(json.dumps(output, ensure_ascii=False, indent=2))

    if args.csv and videos:
        try:
            import pandas as pd
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, "..", "output")
            os.makedirs(output_dir, exist_ok=True)
            df = pd.DataFrame(videos)
            safe_query = "".join(c if c.isalnum() else "_" for c in args.query)[:30]
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(output_dir, f"youtube_{safe_query}_{ts}.csv")
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            print(json.dumps({"csv_saved": csv_path}), file=sys.stderr)
        except ImportError:
            pass


if __name__ == "__main__":
    main()
