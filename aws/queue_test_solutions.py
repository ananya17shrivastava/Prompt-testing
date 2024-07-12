from mysql.connector import Error
import mysql.connector
from typing import List, TypedDict
import uuid
import os
from dotenv import load_dotenv
load_dotenv()
MYSQL_HOST = os.environ.get("MYSQL_HOST")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")

def create_db_connection():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )
    if conn.is_connected():
        print("Connection successful!")
        conn.query('SET GLOBAL connect_timeout=28800')
        conn.query('SET GLOBAL interactive_timeout=28800')
        conn.query('SET GLOBAL wait_timeout=28800')
        return conn
    

class Usecase(TypedDict):
    case_id: str
    name: str
    description: str
    industry_name: str
    industry_category_name: str
    business_area_name: str

def find_usecases() -> List[Usecase]:
    conn = None
    my_cursor = None
    usecases: List[Usecase] = []

    try:
        conn = create_db_connection()
        my_cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            c.id AS case_id,
            c.name AS name,
            c.description AS description,
            ic.name AS industry_category_name,
            i.name AS industry_name,
            ba.name AS business_area_name
        FROM 
            cases c
        JOIN 
            industry_categories ic ON c.industry_category_id = ic.id
        JOIN 
            industries i ON c.industry_id = i.id
        JOIN
            business_areas ba ON c.business_area_id = ba.id
        ORDER BY 
            i.name, ic.name, c.name;
    """

        my_cursor.execute(query)
        results = my_cursor.fetchall()
        print(results)
#  message_dict = {
#         "type": "solutions",
#         "use_case_id":"00010fdf-26d0-4953-bcba-3044faf2b770",
#         "use_case_name" : "AI-facilitated Focus Groups",
#         "use_case_description" : "Employ AI-powered tools to facilitate and analyze focus groups, providing insights into employee perceptions and sentiments.",
#         "industry_name" : "consulting_strategy",
#         "industry_category_name" : "Crisis Management & Turnaround",
#         "timestamp": "2023-05-24T10:30:00Z"
#     }
        for row in results:
            usecases.append({
                "case_id": row['case_id'],
                "name": row['name'].replace('_', ' '),
                "description": row['description'],
                "industry_category_name": row['industry_category_name'].replace('_', ' '),
                "industry_name": row['industry_name'].replace('_', ' '),
                "business_area_name": row['business_area_name'].replace('_', ' ')
            })

    except Error as e:
        print(f"An error occurred while fetching usecases: {str(e)}")
        raise

    finally:
        if my_cursor:
            my_cursor.close()
        if conn:
            conn.close()

    return usecases


