import asyncio
import json
import sys
from pathlib import Path
from notebooklm import NotebookLMClient

# Configure encoding for Windows UTF-8 compatibility
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

async def main():
    print("Connecting to NotebookLM Client...")
    client = await NotebookLMClient.from_storage()
    
    # Load all notebooks to scan
    notebooks_file = Path("tools/_all_notebooks.json")
    if not notebooks_file.exists():
        print("Error: tools/_all_notebooks.json not found.")
        sys.exit(1)
        
    with open(notebooks_file, encoding="utf-8") as f:
        notebooks_data = json.load(f)
        
    async with client:
        total_duplicates_removed = 0
        
        for nb in notebooks_data:
            nb_id = nb["id"]
            nb_title = nb["title"]
            
            print(f"\n========================================")
            print(f"🔍 Checking for Duplicates in: '{nb_title}' (ID: {nb_id})")
            print(f"========================================")
            
            try:
                sources = await client.sources.list(nb_id)
                print(f"Loaded {len(sources)} sources.")
            except Exception as e:
                print(f"⚠️ Error listing sources for {nb_title}: {e}")
                continue
                
            seen_urls = set()
            seen_titles = set()
            
            duplicates_removed = 0
            kept_count = 0
            
            for src in sources:
                src_id = getattr(src, "id", "")
                title = getattr(src, "title", "").strip()
                url = getattr(src, "url", None)
                
                is_url = url is not None and url != "None" and url.strip() != ""
                
                if is_url:
                    # Normalize URL for accurate duplicate comparison (remove trailing slashes, spaces)
                    norm_url = url.strip().lower().rstrip("/")
                    
                    if norm_url in seen_urls:
                        print(f"🚨 Duplicate URL detected! Title: '{title}' | URL: {url} | ID: {src_id}")
                        print(f"   ❌ Deleting duplicate source...")
                        try:
                            success = await client.sources.delete(nb_id, src_id)
                            if success:
                                duplicates_removed += 1
                                total_duplicates_removed += 1
                            else:
                                print(f"   ⚠️ Delete returned False for {src_id}")
                        except Exception as e:
                            print(f"   ⚠️ Error deleting {src_id}: {e}")
                    else:
                        seen_urls.add(norm_url)
                        kept_count += 1
                else:
                    # For text files, check by lowercased title to avoid duplicate text uploads
                    norm_title = title.lower()
                    
                    if norm_title in seen_titles:
                        print(f"🚨 Duplicate Text/Report detected! Title: '{title}' | ID: {src_id}")
                        print(f"   ❌ Deleting duplicate text source...")
                        try:
                            success = await client.sources.delete(nb_id, src_id)
                            if success:
                                duplicates_removed += 1
                                total_duplicates_removed += 1
                            else:
                                print(f"   ⚠️ Delete returned False for {src_id}")
                        except Exception as e:
                            print(f"   ⚠️ Error deleting {src_id}: {e}")
                    else:
                        seen_titles.add(norm_title)
                        kept_count += 1
                        
            print(f"Finished '{nb_title}': Kept {kept_count} unique sources, Deleted {duplicates_removed} duplicates.")
            
        print("\n========================================")
        print(f"🎉 Deduplication Scan Finished! Total duplicates removed: {total_duplicates_removed}")
        print("========================================")

if __name__ == "__main__":
    asyncio.run(main())
