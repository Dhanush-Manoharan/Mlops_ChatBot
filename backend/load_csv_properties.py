import pandas as pd
import random

# Load Zillow data
df = pd.read_csv('other_data/zillow_listings_cleaned.csv')

# Filter for valid properties
df = df[df['property.price.value'].notna()]
df = df[df['property.bedrooms'].notna()]
df = df[df['property.address.streetaddress'].notna()]
df = df[df['property.price.value'] > 50000]  # Filter out rentals
df = df[df['property.bedrooms'] > 0]  # Filter out commercial

def get_properties_from_csv(limit=20):
    """Get random properties from CSV with real prices"""
    sample = df.sample(n=min(limit, len(df)))
    
    properties = []
    for idx, row in sample.iterrows():
        prop = {
            'property_id': f"zillow_{row.get('property.zpid', idx)}",
            'address': str(row.get('property.address.streetaddress', 'Address not available')),
            'city': str(row.get('property.address.city', 'Boston')),
            'state': str(row.get('property.address.state', 'MA')),
            'zipcode': str(row.get('property.address.zipcode', '')),
            'price': float(row['property.price.value']),
            'bedrooms': int(row['property.bedrooms']) if pd.notna(row['property.bedrooms']) else 2,
            'bathrooms': int(row['property.bathrooms']) if pd.notna(row['property.bathrooms']) else 1,
            'beds': int(row['property.bedrooms']) if pd.notna(row['property.bedrooms']) else 2,
            'baths': int(row['property.bathrooms']) if pd.notna(row['property.bathrooms']) else 1,
            'sqft': int(row['property.livingarea']) if pd.notna(row['property.livingarea']) else 1200,
            'image': row.get('property.media.propertyphotolinks.mediumsizelink', 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=400&h=300&fit=crop'),
            'description': f"property | {row.get('property.listing.listingstatus', 'For Sale')} | {row.get('property.address.streetaddress', '')} | {row.get('property.address.city', 'Boston')} | MA",
            'match_score': round(random.uniform(0.7, 0.95), 3)
        }
        properties.append(prop)
    
    return properties

if __name__ == '__main__':
    props = get_properties_from_csv(5)
    for p in props:
        print(f"{p['address']}: ${p['price']:,.0f} - {p['beds']} beds, {p['baths']} baths")
