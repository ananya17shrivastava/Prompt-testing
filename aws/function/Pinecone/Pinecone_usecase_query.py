import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from db.mysql import get_usecase_description,get_opportunity
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
    print(f"Results for query :: {query} are ->")
    # print(results)
    
    for result in results:
        entry_id = result['metadata']['entry_id']
        # print(result)
        usecase_score=result['score']
        opportunity = get_opportunity(entry_id)
        
        
        if opportunity:
            print(f"Opportunity ID: {opportunity['opp_id']}")
            print(f"Case ID: {opportunity['case_id']}")
            print(f"Case Name: {opportunity['case_name']}")
            print(f"Case Description: {opportunity['case_description']}")
            print(f"Business Area ID: {opportunity['business_area_id']}")
            print("Impacted KPIs:")
            for kpi in opportunity['impacted_kpis']:
                print(f"  - {kpi}")
            print(f"Score ::{usecase_score}")
        else:
            print("No opportunity data available")
        
        print("---")

if __name__ == "__main__":
    query = "I want to know which tools are better for automatically writing landing pages and blogs to achieve SEO ranking "
    
    results = query_usecase_pinecone(query)
    print_usecase_results(results['matches'], query)



