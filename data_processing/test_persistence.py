import chromadb

# Connect to ChromaDB
client = chromadb.HttpClient(host="localhost", port="8000")

# List all collections
collections = client.list_collections()

print(f"\n📚 Found {len(collections)} collections:")
for col in collections:
    count = col.count()
    print(f"   - {col.name}: {count} documents")