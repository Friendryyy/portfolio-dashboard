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
    
    # 1. Scan output directory for valid report titles
    output_dir = Path("output")
    valid_titles = set()
    for file in output_dir.glob("*.md"):
        if file.name != ".gitkeep":
            clean_t = _clean_title(file.stem)
            valid_titles.add(clean_t.lower())
            
    print(f"Scanned output/ directory. Found {len(valid_titles)} valid report titles to clean from Stock Notebooks.")
    
    # 2. Load all notebooks
    notebooks_file = Path("tools/_all_notebooks.json")
    if not notebooks_file.exists():
        print("Error: tools/_all_notebooks.json not found.")
        sys.exit(1)
        
    with open(notebooks_file, encoding="utf-8") as f:
        notebooks_data = json.load(f)
        
    master_hub_id = "d4268735-ab02-40c5-80a1-f1b9768befd9"
    
    async with client:
        for nb in notebooks_data:
            nb_id = nb["id"]
            nb_title = nb["title"]
            
            # Skip the Master Hub itself!
            if nb_id == master_hub_id:
                print(f"\n⏭️ Skipping Master Hub ({nb_title})...")
                continue
                
            print(f"\n========================================")
            print(f"🧹 Scanning Stock/Sector Notebook: '{nb_title}' (ID: {nb_id})")
            print(f"========================================")
            
            try:
                sources = await client.sources.list(nb_id)
                print(f"Found {len(sources)} sources in notebook.")
            except Exception as e:
                print(f"⚠️ Error listing sources for {nb_title}: {e}")
                continue
                
            deleted_count = 0
            kept_count = 0
            
            for src in sources:
                src_id = getattr(src, "id", "")
                title = getattr(src, "title", "").strip()
                url = getattr(src, "url", "None")
                
                is_url = url is not None and url != "None" and url.strip() != ""
                is_http_title = title.lower().startswith("http://") or title.lower().startswith("https://")
                is_report_title = title.lower() in valid_titles
                
                # We want to delete it if:
                # 1. It is a report title (matches any .md in output/)
                # 2. Or it is not a URL (meaning it's a text report upload)
                should_delete = is_report_title or (not is_url and not is_http_title)
                
                if should_delete:
                    print(f"❌ Deleting Report: '{title}' (ID: {src_id}) | Reason: ReportTitle={is_report_title}, IsTextReport={not is_url}")
                    try:
                        success = await client.sources.delete(nb_id, src_id)
                        if success:
                            deleted_count += 1
                        else:
                            print(f"   ⚠️ Delete returned False for {src_id}")
                    except Exception as e:
                        print(f"   ⚠️ Error deleting {src_id}: {e}")
                else:
                    print(f"✅ Keeping Source URL: '{title}' (ID: {src_id})")
                    kept_count += 1
                    
            print(f"Finished '{nb_title}': Kept {kept_count} URLs, Deleted {deleted_count} Reports.")

if __name__ == "__main__":
    asyncio.run(main())
