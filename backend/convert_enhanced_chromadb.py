"""
Enhanced ChromaDB Conversion Script
Converts 5 datasets into separate ChromaDB collections for the PropBot:
1. Properties Master - Full property details
2. MBTA Stations - Transit access
3. Public Schools - Education
4. Yelp Businesses - Local amenities
5. Boston Crime - Safety data
"""

import pandas as pd
import numpy as np
from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os

print("[INFO] Loading Sentence Transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

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

batch_size = 100

# ============================================================================
# DATASET 1: PROPERTIES MASTER
# ============================================================================
print("\n" + "="*80)
print("[1/5] PROCESSING PROPERTIES MASTER")
print("="*80)

df_props = pd.read_csv('other_data/properties_master_cleaned.csv')
print(f"[INFO] Loaded {len(df_props)} properties")

collection_props = client.create_collection(name="properties_collection")

documents = []
metadatas = []
ids = []

for idx, row in tqdm(df_props.iterrows(), total=len(df_props), desc="Processing Properties"):
    try:
        # Extract key fields
        address = f"{row.get('st_num', '')} {row.get('st_name', '')}".strip()
        city = str(row.get('city', 'Boston')).strip()
        zipcode = str(row.get('zip_code', '')).strip()

        # Property details
        bedrooms = row.get('bed_rms', None)
        bathrooms = float(row.get('full_bth', 0)) + float(row.get('hlf_bth', 0)) * 0.5 if pd.notna(row.get('full_bth')) else None
        sqft = row.get('living_area', None)
        year_built = row.get('yr_built', None)

        # Financial
        total_value = row.get('total_value', None)
        land_value = row.get('land_value', None)
        bldg_value = row.get('bldg_value', None)
        gross_tax = row.get('_gross_tax_', None)

        # Building info
        bldg_type = str(row.get('bldg_type', '')).strip()
        lu_desc = str(row.get('lu_desc', '')).strip()
        overall_cond = str(row.get('overall_cond', '')).strip()

        # Create rich text description
        doc_text = f"property | {lu_desc} | {address}, {city} {zipcode}"
        if total_value:
            doc_text += f" | Value: ${total_value:,.0f}" if isinstance(total_value, (int, float)) else f" | Value: {total_value}"
        if bedrooms:
            doc_text += f" | {int(bedrooms)} bed"
        if bathrooms:
            doc_text += f", {bathrooms} bath"
        if sqft:
            doc_text += f" | {int(sqft)} sqft"
        if year_built:
            doc_text += f" | Built: {int(year_built)}"
        if bldg_type:
            doc_text += f" | {bldg_type}"
        if overall_cond:
            doc_text += f" | Condition: {overall_cond}"

        # Metadata
        metadata = {
            'type': 'property',
            'address': address,
            'city': city,
            'zipcode': zipcode,
            'bedrooms': int(bedrooms) if pd.notna(bedrooms) else None,
            'bathrooms': float(bathrooms) if pd.notna(bathrooms) else None,
            'sqft': int(sqft) if pd.notna(sqft) else None,
            'year_built': int(year_built) if pd.notna(year_built) else None,
            'total_value': float(total_value) if pd.notna(total_value) and isinstance(total_value, (int, float)) else None,
            'land_value': float(land_value) if pd.notna(land_value) and isinstance(land_value, (int, float)) else None,
            'bldg_value': float(bldg_value) if pd.notna(bldg_value) and isinstance(bldg_value, (int, float)) else None,
            'property_tax': str(gross_tax) if pd.notna(gross_tax) else None,
            'building_type': bldg_type,
            'land_use': lu_desc,
            'condition': overall_cond,
            'pid': str(row.get('pid', ''))
        }

        documents.append(doc_text)
        metadatas.append(metadata)
        ids.append(f"prop_{idx}")

        # Batch insert
        if len(documents) >= batch_size:
            embeddings = model.encode(documents).tolist()
            collection_props.add(documents=documents, metadatas=metadatas, embeddings=embeddings, ids=ids)
            documents, metadatas, ids = [], [], []

    except Exception as e:
        print(f"[WARNING] Error processing property {idx}: {e}")
        continue

# Final batch
if documents:
    embeddings = model.encode(documents).tolist()
    collection_props.add(documents=documents, metadatas=metadatas, embeddings=embeddings, ids=ids)

print(f"[SUCCESS] Properties collection: {collection_props.count()} entries")

# ============================================================================
# DATASET 2: MBTA STATIONS
# ============================================================================
print("\n" + "="*80)
print("[2/5] PROCESSING MBTA STATIONS")
print("="*80)

df_mbta = pd.read_csv('other_data/mbta_stations_cleaned.csv')
print(f"[INFO] Loaded {len(df_mbta)} MBTA stations")

collection_transit = client.create_collection(name="transit_collection")

documents = []
metadatas = []
ids = []

for idx, row in tqdm(df_mbta.iterrows(), total=len(df_mbta), desc="Processing MBTA"):
    try:
        station_name = str(row.get('station_name', '')).strip()
        municipality = str(row.get('municipality', 'Boston')).strip()
        lat = row.get('latitude', None)
        lon = row.get('longitude', None)
        station_id = row.get('station_id', '')

        # Rich text
        doc_text = f"MBTA Station | {station_name} | {municipality}"
        if lat and lon:
            doc_text += f" | Location: ({lat:.4f}, {lon:.4f})"

        metadata = {
            'type': 'transit',
            'station_name': station_name,
            'municipality': municipality,
            'latitude': float(lat) if pd.notna(lat) else None,
            'longitude': float(lon) if pd.notna(lon) else None,
            'station_id': str(station_id)
        }

        documents.append(doc_text)
        metadatas.append(metadata)
        ids.append(f"mbta_{idx}")

        if len(documents) >= batch_size:
            embeddings = model.encode(documents).tolist()
            collection_transit.add(documents=documents, metadatas=metadatas, embeddings=embeddings, ids=ids)
            documents, metadatas, ids = [], [], []

    except Exception as e:
        print(f"[WARNING] Error processing MBTA {idx}: {e}")
        continue

if documents:
    embeddings = model.encode(documents).tolist()
    collection_transit.add(documents=documents, metadatas=metadatas, embeddings=embeddings, ids=ids)

print(f"[SUCCESS] Transit collection: {collection_transit.count()} entries")

# ============================================================================
# DATASET 3: PUBLIC SCHOOLS
# ============================================================================
print("\n" + "="*80)
print("[3/5] PROCESSING PUBLIC SCHOOLS")
print("="*80)

df_schools = pd.read_csv('other_data/public_schools_cleaned.csv')
print(f"[INFO] Loaded {len(df_schools)} public schools")

collection_schools = client.create_collection(name="schools_collection")

documents = []
metadatas = []
ids = []

for idx, row in tqdm(df_schools.iterrows(), total=len(df_schools), desc="Processing Schools"):
    try:
        school_name = str(row.get('sch_name', '')).strip()
        address = str(row.get('address', '')).strip()
        city = str(row.get('city', 'Boston')).strip()
        zipcode = str(row.get('zipcode', '')).strip()
        school_type = str(row.get('sch_type', '')).strip()
        lat = row.get('point_y', None)
        lon = row.get('point_x', None)

        # Rich text
        doc_text = f"Public School | {school_name}"
        if school_type:
            doc_text += f" | Type: {school_type}"
        doc_text += f" | {address}, {city} {zipcode}"

        metadata = {
            'type': 'school',
            'school_name': school_name,
            'address': address,
            'city': city,
            'zipcode': zipcode,
            'school_type': school_type,
            'latitude': float(lat) if pd.notna(lat) else None,
            'longitude': float(lon) if pd.notna(lon) else None,
            'school_id': str(row.get('sch_id', ''))
        }

        documents.append(doc_text)
        metadatas.append(metadata)
        ids.append(f"school_{idx}")

        if len(documents) >= batch_size:
            embeddings = model.encode(documents).tolist()
            collection_schools.add(documents=documents, metadatas=metadatas, embeddings=embeddings, ids=ids)
            documents, metadatas, ids = [], [], []

    except Exception as e:
        print(f"[WARNING] Error processing school {idx}: {e}")
        continue

if documents:
    embeddings = model.encode(documents).tolist()
    collection_schools.add(documents=documents, metadatas=metadatas, embeddings=embeddings, ids=ids)

print(f"[SUCCESS] Schools collection: {collection_schools.count()} entries")

# ============================================================================
# DATASET 4: YELP BUSINESSES
# ============================================================================
print("\n" + "="*80)
print("[4/5] PROCESSING YELP BUSINESSES")
print("="*80)

df_yelp = pd.read_csv('other_data/yelp_businesses_cleaned.csv')
print(f"[INFO] Loaded {len(df_yelp)} Yelp businesses")

collection_amenities = client.create_collection(name="amenities_collection")

documents = []
metadatas = []
ids = []

for idx, row in tqdm(df_yelp.iterrows(), total=len(df_yelp), desc="Processing Yelp"):
    try:
        name = str(row.get('name', '')).strip()
        category = str(row.get('category', '')).strip()
        rating = row.get('rating', None)
        review_count = row.get('review_count', None)
        price = str(row.get('price', '')).strip()
        address = str(row.get('address', '')).strip()
        city = str(row.get('city', 'Boston')).strip()
        lat = row.get('latitude', None)
        lon = row.get('longitude', None)

        # Rich text
        doc_text = f"Business | {name} | Category: {category}"
        if rating:
            doc_text += f" | Rating: {rating}/5"
        if review_count:
            doc_text += f" ({review_count} reviews)"
        if price:
            doc_text += f" | Price: {price}"
        doc_text += f" | {address}, {city}"

        metadata = {
            'type': 'amenity',
            'business_name': name,
            'category': category,
            'rating': float(rating) if pd.notna(rating) else None,
            'review_count': int(review_count) if pd.notna(review_count) else None,
            'price_range': price,
            'address': address,
            'city': city,
            'latitude': float(lat) if pd.notna(lat) else None,
            'longitude': float(lon) if pd.notna(lon) else None,
            'business_id': str(row.get('business_id', ''))
        }

        documents.append(doc_text)
        metadatas.append(metadata)
        ids.append(f"yelp_{idx}")

        if len(documents) >= batch_size:
            embeddings = model.encode(documents).tolist()
            collection_amenities.add(documents=documents, metadatas=metadatas, embeddings=embeddings, ids=ids)
            documents, metadatas, ids = [], [], []

    except Exception as e:
        print(f"[WARNING] Error processing Yelp {idx}: {e}")
        continue

if documents:
    embeddings = model.encode(documents).tolist()
    collection_amenities.add(documents=documents, metadatas=metadatas, embeddings=embeddings, ids=ids)

print(f"[SUCCESS] Amenities collection: {collection_amenities.count()} entries")

# ============================================================================
# DATASET 5: BOSTON CRIME
# ============================================================================
print("\n" + "="*80)
print("[5/5] PROCESSING BOSTON CRIME DATA")
print("="*80)

df_crime = pd.read_csv('other_data/boston_crime_cleaned.csv')
print(f"[INFO] Loaded {len(df_crime)} crime incidents")

# Sample crime data if too large (keep most recent)
if len(df_crime) > 50000:
    print(f"[INFO] Sampling 50,000 most recent incidents from {len(df_crime)}")
    df_crime = df_crime.tail(50000)

collection_crime = client.create_collection(name="crime_collection")

documents = []
metadatas = []
ids = []

for idx, row in tqdm(df_crime.iterrows(), total=len(df_crime), desc="Processing Crime"):
    try:
        offense = str(row.get('offense_description', '')).strip()
        offense_group = str(row.get('offense_code_group', '')).strip()
        district = str(row.get('district', '')).strip()
        street = str(row.get('street', '')).strip()
        date = str(row.get('occurred_on_date', '')).strip()
        year = row.get('year', None)
        lat = row.get('lat', None)
        lon = row.get('long', None)

        # Rich text
        doc_text = f"Crime Incident | {offense}"
        if offense_group:
            doc_text += f" | Category: {offense_group}"
        if district:
            doc_text += f" | District: {district}"
        if street:
            doc_text += f" | Location: {street}"
        if year:
            doc_text += f" | Year: {int(year)}"

        metadata = {
            'type': 'crime',
            'offense': offense,
            'offense_group': offense_group,
            'district': district,
            'street': street,
            'date': date,
            'year': int(year) if pd.notna(year) else None,
            'latitude': float(lat) if pd.notna(lat) else None,
            'longitude': float(lon) if pd.notna(lon) else None,
            'incident_number': str(row.get('incident_number', ''))
        }

        documents.append(doc_text)
        metadatas.append(metadata)
        ids.append(f"crime_{idx}")

        if len(documents) >= batch_size:
            embeddings = model.encode(documents).tolist()
            collection_crime.add(documents=documents, metadatas=metadatas, embeddings=embeddings, ids=ids)
            documents, metadatas, ids = [], [], []

    except Exception as e:
        print(f"[WARNING] Error processing crime {idx}: {e}")
        continue

if documents:
    embeddings = model.encode(documents).tolist()
    collection_crime.add(documents=documents, metadatas=metadatas, embeddings=embeddings, ids=ids)

print(f"[SUCCESS] Crime collection: {collection_crime.count()} entries")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("[COMPLETE] CHROMADB CREATION SUMMARY")
print("="*80)
print(f"Location: {chroma_path}")
print(f"\nCollections created:")
print(f"  1. properties_collection: {collection_props.count():,} entries")
print(f"  2. transit_collection: {collection_transit.count():,} entries")
print(f"  3. schools_collection: {collection_schools.count():,} entries")
print(f"  4. amenities_collection: {collection_amenities.count():,} entries")
print(f"  5. crime_collection: {collection_crime.count():,} entries")
print(f"\nTotal entries: {collection_props.count() + collection_transit.count() + collection_schools.count() + collection_amenities.count() + collection_crime.count():,}")
print("\n[NEXT STEPS]")
print("1. Backup old chroma_data: mv chroma_data chroma_data_backup")
print("2. Replace with new: mv chroma_data_new chroma_data")
print("3. Update rag_pipeline.py to load all 5 collections")
print("4. Test locally")
print("5. Rebuild Docker container")
print("6. Deploy to GCP")
