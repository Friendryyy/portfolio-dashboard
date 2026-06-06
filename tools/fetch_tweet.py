import urllib.request
import re
import sys
import json

mirrors = [
    'nitter.poast.org',
    'nitter.privacydev.net',
    'nitter.moomoo.me',
    'xcancel.com',
    'nitter.net'
]

tweet_id = "2057405513818624123"
username = "investseekers"

found = False
for m in mirrors:
    url = f"https://{m}/{username}/status/{tweet_id}"
    print(f"Trying {url}...", file=sys.stderr)
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
            
            # Simple check to see if we got actual content or generic page
            if "tweet-content" in html or "class=\"tweet-text\"" in html or "class='tweet-text'" in html:
                print(f"Success with {m}!", file=sys.stderr)
                # Let's save the HTML to examine if needed, and print tweet text
                # We can use regex to pull out tweet-content
                content_match = re.search(r'class="tweet-content[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
                if not content_match:
                    content_match = re.search(r"<div class='tweet-text'[^>]*>(.*?)</div>", html, re.DOTALL)
                
                text = ""
                if content_match:
                    text = content_match.group(1)
                    text = re.sub(r'<[^>]+>', ' ', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
                else:
                    text = "Could not extract text using simple regex, but HTML contains tweet-content."
                
                # Check for dates
                date_match = re.search(r'class="tweet-date"[^>]*><a[^>]*title="([^"]+)"', html)
                date_str = date_match.group(1) if date_match else ""
                
                print(json.dumps({
                    "mirror": m,
                    "url": f"https://x.com/{username}/status/{tweet_id}",
                    "username": username,
                    "text": text,
                    "date": date_str,
                    "html_snippet": html[:1000] # just first 1000 chars
                }, ensure_ascii=False, indent=2))
                found = True
                break
            else:
                print(f"Fetch succeeded but no tweet content structure found in HTML from {m}", file=sys.stderr)
    except Exception as e:
        print(f"Failed with {m}: {e}", file=sys.stderr)

if not found:
    print(json.dumps({"error": "Failed to fetch from all mirrors"}), file=sys.stdout)
