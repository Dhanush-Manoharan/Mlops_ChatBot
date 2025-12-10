"""Cloud configuration for ChromaDB"""
import os

def get_chromadb_config():
    """Get ChromaDB configuration"""
    
    if os.getenv('ENVIRONMENT') == 'production':
        # Cloud Run ChromaDB service
        chromadb_host = os.getenv('CHROMADB_HOST', 'chromadb-service')
        chromadb_port = int(os.getenv('CHROMADB_PORT', 8000))
    else:
        # Local development
        chromadb_host = 'localhost'
        chromadb_port = 8000
    
    return chromadb_host, chromadb_port