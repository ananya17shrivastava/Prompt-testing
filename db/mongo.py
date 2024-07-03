from pymongo import MongoClient
import os
import certifi
from datetime import datetime
import json

def mongo_connection():
    MONGO_URI = os.getenv('MONGO_URI')
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client['Model_data']
    data_collection = db['model_data_collection']
    return data_collection

def feed_data_to_mongodb(prompt: str, response, model: str):
    data_collection = mongo_connection()
    
    # Convert response to a JSON-serializable format
    # def convert_to_serializable(obj):
    #     if isinstance(obj, (str, int, float, bool, type(None))):
    #         return obj
    #     elif isinstance(obj, (list, tuple)):
    #         return [convert_to_serializable(item) for item in obj]
    #     elif isinstance(obj, dict):
    #         return {key: convert_to_serializable(value) for key, value in obj.items()}
    #     else:
    #         return str(obj)

    # serializable_response = convert_to_serializable(response)

    document = {
        "trigger_prompt_id": prompt,
        "response_object": response,
        "ai_machine": model,
        "timestamp": datetime.utcnow()
    }
    
    try:
        result = data_collection.insert_one(document)
        
        if result.inserted_id:
            print(f"Data successfully inserted for {model} model with ID: {result.inserted_id}")
        else:
            print("Failed to insert data")
    except Exception as e:
        print(f"Error inserting data: {str(e)}")

# Example usage:
# feed_data_to_mongodb("What is the capital of France?", {"answer": "Paris", "confidence": 0.95}, "GPT-3.5")