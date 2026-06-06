#!/usr/bin/env python3
"""
x_bridge.py — ดึง tweet จากนักวิเคราะห์ใน X ผ่าน xcancel.com (ไม่ต้อง login/API key)

Commands:
  user <username> [--limit N]     tweet ล่าสุดจาก account นั้น
  analysts [--limit N]            tweet จากทุก analyst ที่ติดตาม (default list)
"""

import sys
import json
import re
import argparse
import urllib.request
import urllib.error
from html.parser import HTMLParser

# Analysts ที่ติดตามสำหรับ investment research
DEFAULT_ANALYSTS = [
    "unusual_whales",
    "StockSavvyShay",   # Shay Boloor
    "OptionsHawk",
    "WallStJesus",
    "zerohedge",
]

MIRROR = "https://xcancel.com"


class NitterParser(HTMLParser):
    """Parse xcancel.com/nitter HTML to extract tweets."""

    def __init__(self):
        super().__init__()
        self.tweets = []
        self._current = {}
        self._in_tweet_content = False
        self._in_tweet_date = False
        self._in_tweet_stat = False
        self._depth = 0
        self._content_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        if "timeline-item" in cls and "show-more" not in cls:
            self._current = {"text": "", "date": "", "likes": "", "retweets": "", "url": ""}

        if "tweet-content" in cls:
            self._in_tweet_content = True
            self._content_depth = self._depth

        if tag == "a" and "tweet-date" in cls:
            href = attrs_dict.get("href", "")
            if href:
                self._current["url"] = f"https://x.com{href}"
            self._in_tweet_date = True

        if "icon-heart" in cls:
            self._in_tweet_stat = "likes"
        if "icon-retweet" in cls:
            self._in_tweet_stat = "retweets"

        self._depth += 1

    def handle_endtag(self, tag):
        self._depth -= 1
        if self._in_tweet_content and self._depth <= self._content_depth:
            self._in_tweet_content = False

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        if self._in_tweet_content:
            self._current["text"] += data + " "

        elif self._in_tweet_date:
            self._current["date"] = data
            self._in_tweet_date = False

        elif self._in_tweet_stat == "likes":
            self._current["likes"] = data
            self._in_tweet_stat = False

        elif self._in_tweet_stat == "retweets":
            self._current["retweets"] = data
            self._in_tweet_stat = False

    def handle_entityref(self, name):
        entities = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}
        if self._in_tweet_content:
            self._current["text"] += entities.get(name, "")

    def error(self, message):
        pass


def fetch_user_tweets(username: str, limit: int = 10) -> list:
    """Fetch latest tweets from a user via xcancel.com"""
    url = f"{MIRROR}/{username}"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except urllib.error.URLError as e:
        return [{"error": str(e), "username": username}]

    # Simple regex-based extraction (more reliable than HTML parser for this site)
    tweets = _extract_tweets_regex(html, username, limit)
    return tweets


def _extract_tweets_regex(html: str, username: str, limit: int) -> list:
    """Extract tweets using regex patterns."""
    tweets = []

    # Find tweet blocks
    tweet_blocks = re.findall(
        r'class="tweet-content[^"]*"[^>]*>(.*?)</div>',
        html, re.DOTALL
    )
    dates = re.findall(
        r'class="tweet-date"[^>]*><a[^>]*href="(/[^"]+)"[^>]*title="([^"]+)"',
        html
    )
    stats = re.findall(
        r'class="tweet-stats"[^>]*>(.*?)</div>',
        html, re.DOTALL
    )

    for i, block in enumerate(tweet_blocks[:limit]):
        # Clean HTML tags from tweet text
        text = re.sub(r'<[^>]+>', ' ', block)
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')

        if not text or len(text) < 5:
            continue

        tweet = {
            "username": username,
            "text": text,
            "date": "",
            "url": "",
            "likes": "",
            "retweets": "",
        }

        if i < len(dates):
            tweet["url"] = f"https://x.com{dates[i][0]}"
            tweet["date"] = dates[i][1]

        if i < len(stats):
            stat_text = stats[i]
            likes_match = re.search(r'([\d,]+)\s*(?:like|heart)', stat_text, re.IGNORECASE)
            rt_match = re.search(r'([\d,]+)\s*retweet', stat_text, re.IGNORECASE)
            if likes_match:
                tweet["likes"] = likes_match.group(1)
            if rt_match:
                tweet["retweets"] = rt_match.group(1)

        tweets.append(tweet)

    # Fallback: if regex found nothing, try alternate pattern
    if not tweets:
        alt_blocks = re.findall(
            r'data-tweet-id[^>]*>.*?<div[^>]*class="[^"]*tweet-content[^"]*"[^>]*>(.*?)</div>',
            html, re.DOTALL
        )
        for block in alt_blocks[:limit]:
            text = re.sub(r'<[^>]+>', ' ', block)
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                tweets.append({"username": username, "text": text, "date": "", "url": "", "likes": "", "retweets": ""})

    return tweets


def fetch_all_analysts(limit: int = 5) -> dict:
    """Fetch tweets from all default analysts."""
    results = {}
    for analyst in DEFAULT_ANALYSTS:
        tweets = fetch_user_tweets(analyst, limit)
        results[analyst] = tweets
        # Brief status to stderr
        count = len([t for t in tweets if "error" not in t])
        print(f"  ✓ @{analyst}: {count} tweets", file=sys.stderr)
    return results


def main():
    parser = argparse.ArgumentParser(description="X Bridge — ดึง tweet นักวิเคราะห์สำหรับ investment research")
    subparsers = parser.add_subparsers(dest="command")

    p_user = subparsers.add_parser("user", help="tweet จาก account เดียว")
    p_user.add_argument("username", help="X username (ไม่ต้องใส่ @)")
    p_user.add_argument("--limit", type=int, default=10)

    p_all = subparsers.add_parser("analysts", help="tweet จากทุก analyst ที่ติดตาม")
    p_all.add_argument("--limit", type=int, default=5, help="tweet ต่อคน (default: 5)")

    args = parser.parse_args()

    if args.command == "user":
        result = fetch_user_tweets(args.username, args.limit)
    elif args.command == "analysts":
        result = fetch_all_analysts(args.limit)
    else:
        parser.print_help()
        sys.exit(0)

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
