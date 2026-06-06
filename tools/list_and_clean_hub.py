import asyncio
import json
import sys
from notebooklm import NotebookLMClient

# Configure encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

async def main():
    print("Connecting to NotebookLM Client...")
    client = await NotebookLMClient.from_storage()
    notebook_id = "d4268735-ab02-40c5-80a1-f1b9768befd9"
    
    async with client:
        print(f"Listing sources for Master Hub ({notebook_id})...")
        sources = await client.sources.list(notebook_id)
        
        print(f"\nTotal sources found: {len(sources)}")
        print("\nAvailable sources:")
        for idx, src in enumerate(sources):
            src_id = getattr(src, "id", "Unknown")
            title = getattr(src, "title", "Unknown")
            src_type = getattr(src, "type", "Unknown")
            url = getattr(src, "url", "None")
            print(f"{idx+1}. ID: {src_id} | Title: {title} | Type: {src_type} | URL: {url}")
            
        # Inspect client.sources methods
        print("\nInspecting client.sources methods:")
        for m in dir(client.sources):
            if not m.startswith("_"):
                print(f"  - {m}")
                
        # Also inspect source object itself to see if we can delete it
        if sources:
            print("\nInspecting first source object methods:")
            for m in dir(sources[0]):
                if not m.startswith("_"):
                    print(f"  - {m}")

if __name__ == "__main__":
    asyncio.run(main())
