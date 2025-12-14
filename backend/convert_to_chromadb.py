"""
Convert zillow_listings_cleaned.csv to ChromaDB with embeddings
This will create a new ChromaDB collection with PRICE DATA
"""

import pandas as pd
from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os

print("[INFO] Loading Sentence Transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("[INFO] Reading CSV data...")
df = pd.read_csv('other_data/zillow_listings_cleaned.csv')

print(f"[SUCCESS] Loaded {len(df)} properties")
print(f"[INFO] Columns: {list(df.columns[:10])}...")

# Create new ChromaDB
chroma_path = "chroma_data_new"
if os.path.exists(chroma_path):
    print(f"[WARNING] Removing existing {chroma_path}")
    import shutil
    shutil.rmtree(chroma_path)

client = PersistentClient(
    path=chroma_path,
    settings=Settings(anonymized_telemetry=False)
)
collection = client.create_collection(name="properties")

print("\n[INFO] Converting to ChromaDB with embeddings...")
print("This will take several minutes for 12MB of data...\n")

batch_size = 100
documents = []
metadatas = []
ids = []

for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
    try:
        # Extract key fields
        address = str(row.get('property.address.streetaddress', '')).strip()
        city = str(row.get('property.address.city', '')).strip()
        state = str(row.get('property.address.state', '')).strip()
        zipcode = str(row.get('property.address.zipcode', '')).strip()

        price = row.get('property.price.value', None)
        bedrooms = row.get('property.bedrooms', None)
        bathrooms = row.get('property.bathrooms', None)
        sqft = row.get('property.livingarea', None)
        property_type = str(row.get('property.propertytype', 'Property')).strip()
        listing_status = str(row.get('property.listing.listingstatus', 'For Sale')).strip()

        # Create rich text description for embedding
        doc_text = f"property | {listing_status} | {address}, {city}, {state} {zipcode}"
        if price:
            doc_text += f" | Price: ${price:,.0f}"
        if bedrooms:
            doc_text += f" | {int(bedrooms)} bed"
        if bathrooms:
            doc_text += f", {int(bathrooms)} bath"
        if sqft:
            doc_text += f" | {int(sqft)} sqft"
        doc_text += f" | {property_type}"

        # Create metadata
        metadata = {
            'address': address,
            'city': city,
            'state': state,
            'zipcode': zipcode,
            'price': float(price) if pd.notna(price) else None,
            'bedrooms': int(bedrooms) if pd.notna(bedrooms) else None,
            'bathrooms': int(bathrooms) if pd.notna(bathrooms) else None,
            'sqft': int(sqft) if pd.notna(sqft) else None,
            'property_type': property_type,
            'listing_status': listing_status,
            'zpid': str(row.get('property.zpid', '')),
            'latitude': float(row.get('property.location.latitude', 0)) if pd.notna(row.get('property.location.latitude')) else None,
            'longitude': float(row.get('property.location.longitude', 0)) if pd.notna(row.get('property.location.longitude')) else None,
            'photo_url': str(row.get('property.media.propertyphotolinks.mediumsizelink', ''))
        }

        documents.append(doc_text)
        metadatas.append(metadata)
        ids.append(f"zillow_property_{idx}")

        # Add batch when it reaches batch_size
        if len(documents) >= batch_size:
            embeddings = model.encode(documents).tolist()
            collection.add(
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            documents = []
            metadatas = []
            ids = []

    except Exception as e:
        print(f"[WARNING] Error processing row {idx}: {e}")
        continue

# Add remaining documents
if documents:
    print("\n[INFO] Adding final batch...")
    embeddings = model.encode(documents).tolist()
    collection.add(
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
        ids=ids
    )

print(f"\n[SUCCESS] Successfully created ChromaDB collection with {collection.count()} properties!")
print(f"[INFO] Location: {chroma_path}")
print("\n[NEXT STEPS]")
print("1. Backup old chroma_data: mv chroma_data chroma_data_backup")
print("2. Replace with new: mv chroma_data_new chroma_data")
print("3. Rebuild Docker container")
