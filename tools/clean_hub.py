import asyncio
import json
import sys
import re
from pathlib import Path
from notebooklm import NotebookLMClient

# Configure encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def _clean_title(stem: str) -> str:
    """Convert filename stem to readable title — collapse consecutive separators."""
    return re.sub(r"[\-_]+", " ", stem).strip()

async def main():
    print("Connecting to NotebookLM Client...")
    client = await NotebookLMClient.from_storage()
    notebook_id = "d4268735-ab02-40c5-80a1-f1b9768befd9"
    
    # 1. Scan output directory for valid report titles
    output_dir = Path("output")
    valid_titles = set()
    for file in output_dir.glob("*.md"):
        if file.name != ".gitkeep":
            clean_t = _clean_title(file.stem)
            valid_titles.add(clean_t.lower())
            
    print(f"Scanned output/ directory. Found {len(valid_titles)} valid report titles.")
    
    async with client:
        print(f"Listing sources for Master Hub ({notebook_id})...")
        sources = await client.sources.list(notebook_id)
        print(f"Total sources currently in Master Hub: {len(sources)}")
        
        deleted_count = 0
        kept_count = 0
        
        print("\nEvaluating sources...")
        for src in sources:
            src_id = getattr(src, "id", "")
            title = getattr(src, "title", "").strip()
            url = getattr(src, "url", "None")
            
            # Criteria for deletion:
            # 1. Has a URL (is a web link research source)
            # 2. Or is a bare URL as title (starts with http)
            # 3. Or its clean title is not in our valid_titles set
            is_url = url is not None and url != "None" and url.strip() != ""
            is_http_title = title.lower().startswith("http://") or title.lower().startswith("https://")
            is_valid_report = title.lower() in valid_titles
            
            should_delete = is_url or is_http_title or (not is_valid_report)
            
            if should_delete:
                print(f"❌ Deleting: '{title}' (ID: {src_id}) | Reason: URL={is_url}, HTTP_Title={is_http_title}, Not_in_Output={not is_valid_report}")
                try:
                    success = await client.sources.delete(notebook_id, src_id)
                    if success:
                        deleted_count += 1
                    else:
                        print(f"   ⚠️ Delete returned False for {src_id}")
                except Exception as e:
                    print(f"   ⚠️ Error deleting {src_id}: {e}")
            else:
                print(f"✅ Keeping: '{title}' (ID: {src_id})")
                kept_count += 1
                
        print("\n========================================")
        print(f"Cleanup Completed!")
        print(f"Total Sources Kept: {kept_count}")
        print(f"Total Sources Deleted: {deleted_count}")
        print("========================================")

if __name__ == "__main__":
    asyncio.run(main())
