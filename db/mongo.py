from pymongo import MongoClient
import os
import certifi
from datetime import datetime
import json
from bson import json_util

def mongo_connection():
    MONGO_URI = os.getenv('MONGO_URI')
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client['Model_data']
    data_collection = db['model_data_collection']
    return data_collection

def feed_data_to_mongodb(prompt: str, response, model: str):
    data_collection = mongo_connection()
    
    # Convert response to a BSON-serializable format
    if isinstance(response, str):
        response_data = response
    else:
        try:
            response_data = json.loads(json_util.dumps(response))
        except:
            response_data = str(response)  # Fallback to string representation

    document = {
        "trigger_prompt_id": prompt,
        "response_object": response_data,
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
