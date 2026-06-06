#!/usr/bin/env python3
"""
youtube_bridge.py — YouTube data extraction for investment research
Uses yt-dlp (no login, no API key required)

Commands:
  transcript <url>              Full transcript/subtitles of a video
  info <url>                    Video metadata (title, channel, views, date, description)
  search <query> [--limit N]    Search YouTube, return top N videos with metadata
  comments <url> [--limit N]    Top N comments from a video
  channel <url> [--limit N]     Latest N videos from a channel
"""

import sys
import json
import re
import argparse
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print(json.dumps({"error": "yt-dlp not installed. Run: pip install yt-dlp"}))
    sys.exit(1)


def get_transcript(url: str) -> dict:
    """Download and return full transcript/auto-captions of a video."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "writeautomaticsub": True,
        "writesubtitles": True,
        "subtitleslangs": ["en", "en-orig", "th"],
        "skip_download": True,
        "outtmpl": "/tmp/yt_bridge_%(id)s",
    }

    transcript_text = ""
    video_info = {}

    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            video_info = {
                "id": info.get("id"),
                "title": info.get("title"),
                "channel": info.get("uploader"),
                "duration_sec": info.get("duration"),
                "view_count": info.get("view_count"),
                "upload_date": info.get("upload_date"),
                "url": url,
            }
        except Exception as e:
            return {"error": str(e), "url": url}

    # Try to get subtitles via yt-dlp's subtitle extraction
    sub_opts = {
        "quiet": True,
        "no_warnings": True,
        "writeautomaticsub": True,
        "writesubtitles": True,
        "subtitleslangs": ["en", "en-orig"],
        "skip_download": True,
        "outtmpl": str(Path.home() / "yt_tmp_%(id)s"),
        "subtitlesformat": "json3",
    }

    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        sub_opts["outtmpl"] = os.path.join(tmpdir, "%(id)s")
        sub_opts["progress_hooks"] = []
        sub_opts["noprogress"] = True
        with yt_dlp.YoutubeDL(sub_opts) as ydl:
            try:
                ydl.download([url])
            except Exception:
                pass

        # Find subtitle files
        sub_files = list(Path(tmpdir).glob("*.json3")) + list(Path(tmpdir).glob("*.vtt"))
        for sub_file in sub_files:
            try:
                content = sub_file.read_text(encoding="utf-8")
                if sub_file.suffix == ".json3":
                    transcript_text = _parse_json3_subtitles(content)
                elif sub_file.suffix == ".vtt":
                    transcript_text = _parse_vtt_subtitles(content)
                if transcript_text:
                    break
            except Exception:
                continue

    if not transcript_text:
        transcript_text = "(No transcript available — video may not have captions)"

    return {
        **video_info,
        "transcript": transcript_text,
        "transcript_length": len(transcript_text),
    }


def _parse_json3_subtitles(content: str) -> str:
    """Parse json3 subtitle format into plain text."""
    try:
        data = json.loads(content)
        lines = []
        seen = set()
        for event in data.get("events", []):
            for seg in event.get("segs", []):
                text = seg.get("utf8", "").strip()
                if text and text != "\n" and text not in seen:
                    seen.add(text)
                    lines.append(text)
        return " ".join(lines)
    except Exception:
        return ""


def _parse_vtt_subtitles(content: str) -> str:
    """Parse WebVTT subtitle format into plain text."""
    lines = content.split("\n")
    text_lines = []
    seen = set()
    for line in lines:
        line = line.strip()
        # Skip headers, timestamps, empty lines
        if not line or line.startswith("WEBVTT") or line.startswith("NOTE") or "-->" in line:
            continue
        if re.match(r"^\d+$", line):
            continue
        # Remove HTML tags
        clean = re.sub(r"<[^>]+>", "", line).strip()
        if clean and clean not in seen:
            seen.add(clean)
            text_lines.append(clean)
    return " ".join(text_lines)


def get_info(url: str) -> dict:
    """Get video metadata without downloading."""
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                "id": info.get("id"),
                "title": info.get("title"),
                "channel": info.get("uploader"),
                "channel_url": info.get("uploader_url"),
                "duration_sec": info.get("duration"),
                "view_count": info.get("view_count"),
                "like_count": info.get("like_count"),
                "comment_count": info.get("comment_count"),
                "upload_date": info.get("upload_date"),
                "description": (info.get("description") or "")[:1000],
                "tags": info.get("tags", [])[:20],
                "url": url,
            }
        except Exception as e:
            return {"error": str(e), "url": url}


def search_youtube(query: str, limit: int = 5) -> list:
    """Search YouTube and return top N videos with metadata."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "default_search": f"ytsearch{limit}",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            videos = []
            for entry in result.get("entries", []):
                if entry:
                    videos.append({
                        "title": entry.get("title"),
                        "channel": entry.get("uploader") or entry.get("channel"),
                        "duration_sec": entry.get("duration"),
                        "view_count": entry.get("view_count"),
                        "upload_date": entry.get("upload_date"),
                        "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                        "id": entry.get("id"),
                    })
            return videos
        except Exception as e:
            return [{"error": str(e), "query": query}]


def get_comments(url: str, limit: int = 20) -> dict:
    """Get top comments from a video."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "getcomments": True,
        "extractor_args": {"youtube": {"comment_sort": ["top"], "max_comments": [str(limit)]}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            comments = []
            for c in (info.get("comments") or [])[:limit]:
                comments.append({
                    "author": c.get("author"),
                    "text": (c.get("text") or "")[:500],
                    "like_count": c.get("like_count"),
                    "timestamp": c.get("timestamp"),
                })
            return {
                "title": info.get("title"),
                "url": url,
                "comment_count_total": info.get("comment_count"),
                "comments": comments,
            }
        except Exception as e:
            return {"error": str(e), "url": url}


def get_channel_videos(url: str, limit: int = 10) -> list:
    """Get latest N videos from a channel."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": limit,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(url, download=False)
            videos = []
            for entry in (result.get("entries") or [])[:limit]:
                if entry:
                    videos.append({
                        "title": entry.get("title"),
                        "duration_sec": entry.get("duration"),
                        "view_count": entry.get("view_count"),
                        "upload_date": entry.get("upload_date"),
                        "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                        "id": entry.get("id"),
                    })
            return videos
        except Exception as e:
            return [{"error": str(e), "url": url}]


def main():
    parser = argparse.ArgumentParser(description="YouTube Bridge for Investment Research")
    subparsers = parser.add_subparsers(dest="command")

    # transcript
    p_trans = subparsers.add_parser("transcript", help="Get full transcript of a video")
    p_trans.add_argument("url", help="YouTube video URL")

    # info
    p_info = subparsers.add_parser("info", help="Get video metadata")
    p_info.add_argument("url", help="YouTube video URL")

    # search
    p_search = subparsers.add_parser("search", help="Search YouTube")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", type=int, default=5, help="Number of results (default: 5)")

    # comments
    p_comments = subparsers.add_parser("comments", help="Get top comments")
    p_comments.add_argument("url", help="YouTube video URL")
    p_comments.add_argument("--limit", type=int, default=20, help="Number of comments (default: 20)")

    # channel
    p_channel = subparsers.add_parser("channel", help="Get latest videos from channel")
    p_channel.add_argument("url", help="YouTube channel URL")
    p_channel.add_argument("--limit", type=int, default=10, help="Number of videos (default: 10)")

    args = parser.parse_args()

    if args.command == "transcript":
        result = get_transcript(args.url)
    elif args.command == "info":
        result = get_info(args.url)
    elif args.command == "search":
        result = search_youtube(args.query, args.limit)
    elif args.command == "comments":
        result = get_comments(args.url, args.limit)
    elif args.command == "channel":
        result = get_channel_videos(args.url, args.limit)
    else:
        parser.print_help()
        sys.exit(0)

    sys.stdout.buffer.write(json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
