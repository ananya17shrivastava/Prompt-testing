import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from db.mysql import get_usecase_description
from dotenv import load_dotenv
load_dotenv()

def query_usecase_pinecone(query_text: str, top_k: int = 10) -> Dict:
    pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
    index = pc.Index('use-cases')
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query_text).tolist()

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    return results


def print_usecase_results(results: List[Dict], query: str):
    
    print(f"Results for  for query :: {query} are ->")
    
    for result in results:

        usecase_name=result['metadata']['usecase_name']
        usecase_score=result['score']
        id=result['id']
        usecase_description=get_usecase_description(id)
        print(f"Usecase name: {usecase_name}")
        print(f"Score: {usecase_score}")
        print(f"ID: {id}")
        print(f"Description: {usecase_description}")
        print("---")

if __name__ == "__main__":
    query = "I want to know which tools are better for automatically writing landing pages and blogs to achieve SEO ranking "
    
    results = query_usecase_pinecone(query)
    print_usecase_results(results['matches'], query)



