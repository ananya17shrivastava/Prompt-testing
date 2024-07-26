from db.mysql import find_pinecone_business_areas
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import os

# Fetch business areas
business_areas = find_pinecone_business_areas()
print(len(business_areas))

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

# Create or connect to an index
index_name = 'business-areas'
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384, 
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1'
        ) 
    )

# Get the index
index = pc.Index(index_name)

# Function to upsert in batches
def upsert_in_batches(vectors, batch_size=100):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)
        print(f"Uploaded batch {i//batch_size + 1} of {len(vectors)//batch_size + 1}")

# Process and upsert in batches
batch_size = 100
for i in range(0, len(business_areas), batch_size):
    batch = business_areas[i:i+batch_size]
    
    # Generate embeddings for this batch
    embeddings = [model.encode(area['business_area_name']) for area in batch]
    
    # Prepare vectors for this batch
    vectors_to_upsert = [
        (area['business_area_id'], 
         embedding.tolist(), 
         {"business_area_name": area['business_area_name'], "entry_id": area['entry_id']})
        for area, embedding in zip(batch, embeddings)
    ]
    
    # Upsert this batch
    upsert_in_batches(vectors_to_upsert)

print("All business areas uploaded to Pinecone")