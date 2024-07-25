import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from db.mysql import get_business_description
from dotenv import load_dotenv
load_dotenv()

def query_business_pinecone(query_text: str, top_k: int = 10) -> Dict:
    pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
    index = pc.Index('business-areas')
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query_text).tolist()

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    return results


def print_business_results(results: List[Dict], query: str):
    
    print(f"Results for  for query :: {query} are ->")
    
    for result in results:

        business_area_name=result['metadata']['business_area_name']
        business_area_score=result['score']
        id=result['id']
        entry_id=result['entry_id']

        business_area_description=get_business_description(id)
        print(f"Business Area: {business_area_name}")
        print(f"Score: {business_area_score}")
        print(f"ID: {id}")
        print(f"Description: {business_area_description}")
        print(f"Entry id: {entry_id}")

        print("---")

if __name__ == "__main__":
    query = "I want to know which tools are better for automatically writing landing pages and blogs to achieve SEO ranking "
    
    results = query_business_pinecone(query)
    print_business_results(results['matches'], query)

