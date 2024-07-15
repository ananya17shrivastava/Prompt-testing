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
        WHERE 
            i.id = 'be4f80ec-3678-4bf2-b6b6-f5e69301a95c'
        ORDER BY 
            i.name, ic.name, c.name;
    """

        my_cursor.execute(query)
        results = my_cursor.fetchall()
        # print(results)
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


class AISolution(TypedDict):
    solution_id: str
    solution_name: str
    usecase_name: str
    usecase_description: str
    industry_category_name: str
    industry_name: str
    case_id: str  

def find_aisolutions() -> List[AISolution]:
    conn = None
    my_cursor = None
    ai_solutions: List[AISolution] = []

    try:
        conn = create_db_connection()
        my_cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                s.id AS solution_id,
                s.name AS solution_name,
                c.name AS usecase_name,
                c.id AS case_id,
                c.description AS usecase_description,
                ic.name AS industry_category_name,
                i.name AS industry_name
            FROM 
                solutions s
            JOIN 
                case_to_solution cts ON s.id = cts.solution_id
            JOIN 
                cases c ON cts.case_id = c.id
            JOIN 
                industries i ON c.industry_id = i.id
            JOIN 
                industry_categories ic ON c.industry_category_id = ic.id
            WHERE 
                s.ai_generated = 1 AND i.id='be4f80ec-3678-4bf2-b6b6-f5e69301a95c';
        """

        my_cursor.execute(query)
        results = my_cursor.fetchall()

        for row in results:
            ai_solutions.append({
                "solution_id": row['solution_id'],
                "solution_name": row['solution_name'].replace('_', ' '),
                "case_id": row['case_id'],  
                "usecase_name": row['usecase_name'].replace('_', ' '),
                "usecase_description": row['usecase_description'],
                "industry_category_name": row['industry_category_name'].replace('_', ' '),
                "industry_name": row['industry_name'].replace('_', ' '),
                
            })

    except Error as e:
        print(f"An error occurred while fetching AI solutions: {str(e)}")
        raise

    finally:
        if my_cursor:
            my_cursor.close()
        # if conn:
        #     conn.close()

    return ai_solutions


class BusinessArea(TypedDict):
    business_area_id: str
    business_area_name: str
    industry_category_id: str
    industry_category_name: str
    industry_id: str
    industry_name: str

def find_business_areas() -> List[BusinessArea]:
    conn = None
    my_cursor = None
    business_areas: List[BusinessArea] = []

    try:
        conn = create_db_connection()
        my_cursor = conn.cursor()
        
        query = """
            SELECT 
            ba.id AS business_area_id,
            ba.name AS business_area_name,
            ic.id AS industry_category_id,
            ic.name AS industry_category_name,
            i.id AS industry_id,
            i.name AS industry_name
        FROM 
            business_areas ba
        LEFT JOIN 
            industry_categories ic ON ba.industry_category_id = ic.id COLLATE utf8mb4_unicode_ci
        JOIN 
            industries i ON ba.industry_id = i.id COLLATE utf8mb4_unicode_ci
        WHERE 
            i.id IN (
                '744bec80-9eda-4319-bfd6-51d50d407c3e',
                '6b278ac5-8a12-4ecc-a448-05beaec6ae9b',
                '53a07e49-d224-4c67-ae1e-8d8410630b92',
                '320e36b3-eba7-4201-972b-a36970120942',
                'c5a191e5-ebe5-439f-86b5-51606cff5a46',
                'cb6269d0-65a4-4d8c-a741-bc84b7db2f70',
                '114c8b66-98a3-4c78-ba37-6a7b857f21ea',
                'f8ecc82e-0839-4c00-9866-ac47826445f9',
                'c27cfb4d-1515-4be5-9381-7f650c43cc0b',
                'a0188fab-ca9b-47c4-a58a-360b996d62fb',
                'cc75308c-3100-4e9a-bb9c-d4c0cef9e326',
                '650f1811-a8be-496c-b82a-2a5d26592218',
                '1946ba38-0f21-402f-838e-800060d7ce54',
                'fb371a14-00c8-471c-9376-fd133c09519e',
                'be4f80ec-3678-4bf2-b6b6-f5e69301a95c'
            )
        ORDER BY 
            i.name, ic.name, ba.name;
        """

        my_cursor.execute(query)

        results = my_cursor.fetchall()
        print(results)

        for (business_area_id, business_area_name, industry_category_id, 
             industry_category_name, industry_id, industry_name) in results:
            business_areas.append({
                "business_area_id": business_area_id,
                "business_area_name": business_area_name.replace('_', ' '),
                "industry_category_id": industry_category_id,
                "industry_category_name": industry_category_name,
                "industry_id": industry_id,
                "industry_name": industry_name.replace('_', ' ')
            })

    except Error as e:
        print(f"An error occurred while fetching business areas: {str(e)}")
        raise

    finally:
        if my_cursor:
            my_cursor.close()
        if conn:
            conn.close()

    return business_areas
