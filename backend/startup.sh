#!/bin/bash
set -e

echo "=========================================="
echo "🚀 PropBot Backend Startup"
echo "=========================================="

# ALWAYS download ChromaDB data from GCS (remove old check)
echo "📦 Downloading ChromaDB data from GCS bucket..."
echo "   Source: gs://propbot-chromadb-data-uscentral/"
echo "   Target: /app/chroma_data/"

# Remove old data if exists
rm -rf /app/chroma_data/*

gsutil -m rsync -r gs://propbot-chromadb-data-uscentral/ /app/chroma_data/

# Verify download
if [ -f "/app/chroma_data/chroma.sqlite3" ]; then
    SIZE=$(du -sh /app/chroma_data | cut -f1)
    echo "✅ ChromaDB data downloaded successfully ($SIZE)"
else
    echo "❌ ERROR: Failed to download ChromaDB data!"
    exit 1
fi

echo ""
echo "📂 ChromaDB data contents:"
ls -lh /app/chroma_data/ | head -10

echo ""
echo "=========================================="
echo "🎉 Startup complete! Starting FastAPI..."
echo "=========================================="