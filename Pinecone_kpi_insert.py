from db.mysql import get_kpi
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import os

# Fetch business areas
kpis = get_kpi()
print(len(kpis))

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

# Create or connect to an index
index_name = 'kpis'
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
    total_batches = (len(vectors) + batch_size - 1) // batch_size
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)
        current_batch = i // batch_size + 1
        print(f"Uploaded batch {current_batch} of {total_batches}")

# Process and upsert in batches
batch_size = 100
for i in range(0, len(kpis), batch_size):
    batch = kpis[i:i+batch_size]
    
    # Generate embeddings for this batch
    embeddings = [model.encode(area['kpi_name']) for area in batch]
    
    # Prepare vectors for this batch
    vectors_to_upsert = [
        (area['id'], 
         embedding.tolist(), 
         {"kpi_name": area['kpi_name']})
        for area, embedding in zip(batch, embeddings)
    ]
    
    # Upsert this batch
    upsert_in_batches(vectors_to_upsert)

print("All kpis uploaded to Pinecone")