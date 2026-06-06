import asyncio
import inspect
from notebooklm import NotebookLMClient

async def main():
    client = await NotebookLMClient.from_storage()
    async with client:
        # Inspect delete method signature
        sig = inspect.signature(client.sources.delete)
        print("Signature of client.sources.delete:", sig)
        print("Parameters:", list(sig.parameters.keys()))

if __name__ == "__main__":
    asyncio.run(main())
