from typing import List, TypedDict
from db.mysql import find_pinecone_usecases
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import os


# Fetch usecases
usecases = find_pinecone_usecases()
print(len(usecases))

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

# Create or connect to an index
index_name = 'use-cases'
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
for i in range(0, len(usecases), batch_size):
    batch = usecases[i:i+batch_size]
    
    # Generate embeddings for this batch
    embeddings = [model.encode(usecase['usecase_name']) for usecase in batch]
    
    # Prepare vectors for this batch
    vectors_to_upsert = [
        (usecase['case_id'], 
         embedding.tolist(), 
         {"usecase_name": usecase['usecase_name'], "entry_id": usecase['entry_id']})
        for usecase, embedding in zip(batch, embeddings)
    ]
    
    # Upsert this batch
    upsert_in_batches(vectors_to_upsert)

print("All usecases uploaded to Pinecone")