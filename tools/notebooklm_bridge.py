#!/usr/bin/env python3
"""
NotebookLM Bridge — CLI wrapper for Claude Code to interact with Google NotebookLM.
Uses notebooklm-py (https://github.com/teng-lin/notebooklm-py)

Usage:
    python tools/notebooklm_bridge.py list
    python tools/notebooklm_bridge.py find "ASTS"
    python tools/notebooklm_bridge.py create "ASTS Analysis 2026"
    python tools/notebooklm_bridge.py query <notebook_id> "What is the moat?"
    python tools/notebooklm_bridge.py add-url <notebook_id> <url>
    python tools/notebooklm_bridge.py add-urls-batch <notebook_id> <file>   ← auto-dedup
    python tools/notebooklm_bridge.py add-report <notebook_id> <file.md>    ← skip if title exists
    python tools/notebooklm_bridge.py add-text <notebook_id> --title "Title" --file <path>
    python tools/notebooklm_bridge.py list-sources <notebook_id>
"""

import asyncio
import json
import sys
import argparse
import os
import re
from pathlib import Path

# Force UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError with emoji/Thai)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def output(data):
    """Print JSON to stdout for Claude Code to parse."""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def error_exit(msg: str, code: int = 1):
    print(json.dumps({"error": msg}, ensure_ascii=False), file=sys.stderr)
    sys.exit(code)


async def get_client():
    try:
        from notebooklm import NotebookLMClient
    except ImportError:
        error_exit(
            "notebooklm-py not installed. Run: pip install \"notebooklm-py[browser]\" "
            "then: playwright install chromium  then: notebooklm login"
        )

    try:
        client = await NotebookLMClient.from_storage()
        return client
    except Exception as e:
        error_exit(
            f"Auth failed: {e}\n"
            "Run 'notebooklm login' in terminal to authenticate first."
        )


async def _fetch_existing_sources(client, notebook_id: str) -> tuple[set, set]:
    """
    Returns (existing_urls, existing_titles) — both lowercased for comparison.
    Falls back to empty sets if the API doesn't support listing.
    """
    existing_urls: set[str] = set()
    existing_titles: set[str] = set()
    try:
        sources = await client.sources.list(notebook_id)
        for s in sources:
            url = str(getattr(s, "url", "") or "").strip()
            title = str(getattr(s, "title", "") or "").strip()
            if url:
                existing_urls.add(url)
            if title:
                existing_titles.add(title.lower())
    except Exception:
        # If the API doesn't support listing, proceed without dedup
        pass
    return existing_urls, existing_titles


async def cmd_list():
    async with await get_client() as client:
        notebooks = await client.notebooks.list()
        result = [
            {"id": nb.id, "name": nb.title or nb.id, "source_count": getattr(nb, "source_count", "?")}
            for nb in notebooks
        ]
        output({"notebooks": result, "count": len(result)})


async def cmd_find(query: str):
    async with await get_client() as client:
        notebooks = await client.notebooks.list()
        q = query.lower()
        matches = [
            {"id": nb.id, "name": nb.title or nb.id}
            for nb in notebooks
            if q in (nb.title or "").lower() or q in nb.id.lower()
        ]
        output({"query": query, "matches": matches, "count": len(matches)})


async def cmd_create(name: str):
    async with await get_client() as client:
        nb = await client.notebooks.create(name)
        output({"created": True, "id": nb.id, "name": name})


async def cmd_query(notebook_id: str, question: str):
    async with await get_client() as client:
        response = await client.chat.ask(notebook_id, question)
        answer = response.answer if hasattr(response, "answer") else str(response)
        citations = []
        if hasattr(response, "citations"):
            for c in response.citations:
                citations.append({
                    "text": getattr(c, "text", ""),
                    "source": getattr(c, "source_title", "")
                })
        output({"notebook_id": notebook_id, "question": question, "answer": answer, "citations": citations})


async def cmd_list_sources(notebook_id: str):
    """List all sources in a notebook — useful for manual dedup inspection."""
    async with await get_client() as client:
        try:
            sources = await client.sources.list(notebook_id)
            result = []
            for s in sources:
                result.append({
                    "id": getattr(s, "id", "?"),
                    "title": getattr(s, "title", ""),
                    "url": getattr(s, "url", None),
                    "type": getattr(s, "type", "?"),
                })
            output({
                "notebook_id": notebook_id,
                "source_count": len(result),
                "sources": result
            })
        except Exception as e:
            error_exit(f"Could not list sources: {e}")


async def cmd_add_url(notebook_id: str, url: str, wait: bool = False):
    try:
        from notebooklm.exceptions import RPCTimeoutError
    except ImportError:
        RPCTimeoutError = Exception

    async with await get_client() as client:
        # Check for duplicate before adding
        existing_urls, _ = await _fetch_existing_sources(client, notebook_id)
        if url.strip() in existing_urls:
            output({
                "added": False,
                "skipped": True,
                "reason": "already exists in notebook",
                "url": url
            })
            return

        try:
            source = await client.sources.add_url(notebook_id, url, wait=wait)
            output({
                "added": True,
                "notebook_id": notebook_id,
                "url": url,
                "source_id": getattr(source, "id", "?"),
                "title": getattr(source, "title", url)
            })
        except RPCTimeoutError:
            output({
                "added": False,
                "skipped": True,
                "reason": "timeout — NotebookLM took too long to fetch this URL (paywalled or slow site)",
                "url": url
            })
        except Exception as e:
            output({
                "added": False,
                "skipped": True,
                "reason": str(e),
                "url": url
            })


async def cmd_add_urls_batch(notebook_id: str, urls: list):
    """
    Add multiple URLs — auto-dedup against existing sources.
    Skips URLs already in the notebook, reports X added / Y skipped.
    """
    try:
        from notebooklm.exceptions import RPCTimeoutError
    except ImportError:
        RPCTimeoutError = Exception

    async with await get_client() as client:
        # PRE-CHECK: fetch existing URLs to avoid duplicates
        existing_urls, _ = await _fetch_existing_sources(client, notebook_id)

        new_urls = [u for u in urls if u.strip() not in existing_urls]
        already_existed = [u for u in urls if u.strip() in existing_urls]

        if already_existed:
            for u in already_existed:
                print(json.dumps({"progress": f"⏭️  Skipped (already exists): {u[:80]}"}), file=sys.stderr)

        results = []
        for url in new_urls:
            try:
                source = await client.sources.add_url(notebook_id, url, wait=False)
                results.append({
                    "added": True,
                    "url": url,
                    "source_id": getattr(source, "id", "?")
                })
                print(json.dumps({"progress": f"✅ Added: {url[:80]}"}), file=sys.stderr)
            except RPCTimeoutError:
                results.append({
                    "added": False,
                    "skipped": True,
                    "reason": "timeout",
                    "url": url
                })
                print(json.dumps({"progress": f"⏭️  Skipped (timeout): {url[:80]}"}), file=sys.stderr)
            except Exception as e:
                # Primary URL failed — try archive.org fallback (handles CNBC/Bloomberg/paywalls)
                archive_url = _to_archive_url(url)
                try:
                    source = await client.sources.add_url(notebook_id, archive_url, wait=False)
                    results.append({
                        "added": True,
                        "url": url,
                        "archive_fallback": archive_url,
                        "source_id": getattr(source, "id", "?")
                    })
                    print(json.dumps({"progress": f"📦 Added via archive.org: {url[:70]}"}), file=sys.stderr)
                except Exception as e2:
                    results.append({
                        "added": False,
                        "skipped": True,
                        "reason": f"primary: {str(e)[:50]} | archive: {str(e2)[:50]}",
                        "url": url
                    })
                    print(json.dumps({"progress": f"❌ Failed (incl. archive.org): {url[:60]}"}), file=sys.stderr)

        added = [r for r in results if r["added"]]
        failed = [r for r in results if not r["added"]]

        output({
            "notebook_id": notebook_id,
            "total_in_file": len(urls),
            "already_existed": len(already_existed),
            "attempted": len(new_urls),
            "added_count": len(added),
            "skipped_count": len(failed),
            "added": added,
            "skipped_existing": already_existed,
            "skipped_failed": failed,
            "summary": f"{len(added)} added, {len(already_existed)} skipped (already existed), {len(failed)} failed"
        })


def _to_archive_url(url: str) -> str:
    """Return archive.org fallback URL for a blocked/paywalled URL.
    Uses the open-ended wildcard redirect (latest available snapshot).
    """
    url = url.strip()
    if "web.archive.org" in url:
        return url  # already an archive URL, don't double-wrap
    return f"https://web.archive.org/web/{url}"


def _read_file_safe(path: Path) -> str:
    """Read file content with UTF-8 fallback to cp1252 on Windows."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"[notebooklm] WARNING: UTF-8 decode failed for {path.name}, retrying as cp1252", file=sys.stderr)
        return path.read_text(encoding="cp1252", errors="replace")


def _clean_title(stem: str) -> str:
    """Convert filename stem to readable title — collapse consecutive separators."""
    return re.sub(r"[\-_]+", " ", stem).strip()


async def cmd_add_report(notebook_id: str, file_path: str):
    """
    Upload a markdown report as a text source.
    Auto-skips if a source with the same title already exists.
    """
    path = Path(file_path)
    if not path.exists():
        error_exit(f"File not found: {file_path}")

    content = _read_file_safe(path)
    title = _clean_title(path.stem)

    async with await get_client() as client:
        # PRE-CHECK: skip if report title already exists in this notebook
        _, existing_titles = await _fetch_existing_sources(client, notebook_id)
        if title.lower() in existing_titles:
            output({
                "added": False,
                "skipped": True,
                "reason": "report with same title already exists in notebook",
                "notebook_id": notebook_id,
                "file": file_path,
                "title": title
            })
            return

        source = await client.sources.add_text(
            notebook_id,
            title,
            content,
            wait=True
        )
        output({
            "added": True,
            "notebook_id": notebook_id,
            "file": file_path,
            "title": title,
            "source_id": getattr(source, "id", "?")
        })


async def cmd_add_text(notebook_id: str, title: str, file_path: str):
    path = Path(file_path)
    if not path.exists():
        error_exit(f"File not found: {file_path}")

    content = _read_file_safe(path)

    async with await get_client() as client:
        source = await client.sources.add_text(
            notebook_id,
            title,
            content,
            wait=True
        )
        output({
            "added": True,
            "notebook_id": notebook_id,
            "title": title,
            "source_id": getattr(source, "id", "?")
        })


def main():
    parser = argparse.ArgumentParser(description="NotebookLM CLI Bridge for Claude Code")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List all notebooks")

    p_find = subparsers.add_parser("find", help="Find notebooks by name")
    p_find.add_argument("query", help="Search query")

    p_create = subparsers.add_parser("create", help="Create a new notebook")
    p_create.add_argument("name", help="Notebook name")

    p_query = subparsers.add_parser("query", help="Ask a question to a notebook")
    p_query.add_argument("notebook_id", help="Notebook ID")
    p_query.add_argument("question", help="Question to ask")

    p_add_url = subparsers.add_parser("add-url", help="Add a URL source (auto-dedup)")
    p_add_url.add_argument("notebook_id", help="Notebook ID")
    p_add_url.add_argument("url", help="URL to add")

    p_add_urls = subparsers.add_parser(
        "add-urls-batch",
        help="Add URLs from file — auto-dedup: skips URLs already in notebook"
    )
    p_add_urls.add_argument("notebook_id", help="Notebook ID")
    p_add_urls.add_argument("file", help="Path to text file with one URL per line")

    p_add_report = subparsers.add_parser(
        "add-report",
        help="Add markdown report as source — skips if same title already exists"
    )
    p_add_report.add_argument("notebook_id", help="Notebook ID")
    p_add_report.add_argument("file", help="Path to .md report file")

    p_add_text = subparsers.add_parser("add-text", help="Add text file with custom title")
    p_add_text.add_argument("notebook_id", help="Notebook ID")
    p_add_text.add_argument("--title", required=True, help="Source title")
    p_add_text.add_argument("--file", required=True, dest="file_path", help="Path to text file")

    p_list_sources = subparsers.add_parser(
        "list-sources",
        help="List all sources in a notebook (for inspection / manual dedup)"
    )
    p_list_sources.add_argument("notebook_id", help="Notebook ID")

    args = parser.parse_args()

    if args.command == "list":
        asyncio.run(cmd_list())
    elif args.command == "find":
        asyncio.run(cmd_find(args.query))
    elif args.command == "create":
        asyncio.run(cmd_create(args.name))
    elif args.command == "query":
        asyncio.run(cmd_query(args.notebook_id, args.question))
    elif args.command == "add-url":
        asyncio.run(cmd_add_url(args.notebook_id, args.url))
    elif args.command == "add-urls-batch":
        with open(args.file, encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        asyncio.run(cmd_add_urls_batch(args.notebook_id, urls))
    elif args.command == "add-report":
        asyncio.run(cmd_add_report(args.notebook_id, args.file))
    elif args.command == "add-text":
        asyncio.run(cmd_add_text(args.notebook_id, args.title, args.file_path))
    elif args.command == "list-sources":
        asyncio.run(cmd_list_sources(args.notebook_id))


if __name__ == "__main__":
    main()
