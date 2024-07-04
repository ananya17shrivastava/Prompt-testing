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


# def get_industryid(industryname: str) -> str:
#     conn = None
#     my_cursor = None
#     industry_id = None

#     try:
#         conn = create_db_connection()
#         my_cursor = conn.cursor()

#         industry = industryname.replace(' ', '_')
#         industry_query = "SELECT id FROM industries WHERE name = %s"
#         my_cursor.execute(industry_query, (industry,))
#         industry_result = my_cursor.fetchone()

#         if not industry_result:
#             print(f"Industry '{industry}' not found in the database.")
#             return None

#         industry_id = industry_result[0]

#     except Error as e:
#         print(f"An error occurred while fetching industry ID: {str(e)}")
#         return None

#     finally:
#         if my_cursor:
#             my_cursor.close()
#         if conn:
#             conn.close()

#     return industry_id


class Industry(TypedDict):
    id: str
    name: str


def find_industries() -> List[Industry]:
    conn = None
    my_cursor = None
    industries = []

    try:
        conn = create_db_connection()
        my_cursor = conn.cursor()

        my_cursor.execute("SELECT id,name FROM industries")
        names = my_cursor.fetchall()

        for id, name in names:
            name = name.replace('_', ' ')
            industries.append({"id": id, "name": name})

    except Error as e:
        print(f"An error occurred while fetching industries: {str(e)}")
        raise Error

    finally:
        if my_cursor:
            my_cursor.close()
        if conn:
            conn.close()

    return industries


def delete_all_industry_category(industry_id: str):
    conn = create_db_connection()
    my_cursor = conn.cursor()
    check_query = """
        DELETE FROM industry_categories
        WHERE industry_id = %s
    """
    my_cursor.execute(check_query, (industry_id,))
    conn.commit()
    print("Deleted industry categories")
    my_cursor.close()
    conn.close()


def insert_industry_category(industry_id: str, name: str, product_services: str):
    conn = create_db_connection()
    my_cursor = conn.cursor()

    try:
        check_query = """
            SELECT id FROM industry_categories 
            WHERE industry_id = %s and name = %s
        """
        my_cursor.execute(check_query, (industry_id, name,))
        existing_record = my_cursor.fetchone()

        if existing_record:
            update_query = """
                UPDATE industry_categories 
                SET products_and_services = %s
                WHERE industry_id = %s and name = %s
            """
            my_cursor.execute(update_query, (product_services, industry_id, name))
            print(f"Updated: Name: {name}, Industry ID: {industry_id}, Value: {product_services}")
        else:
            category_id = str(uuid.uuid4())
            insert_query = """
                INSERT INTO industry_categories 
                (id, name, created_at, source_id, industry_id, products_and_services,ai_generated) 
                VALUES (%s, %s, NOW(), NULL, %s, %s,%s)
            """
            print(f"Inserting Name: {name}, Industry ID: {industry_id}, Value: {product_services}")
            my_cursor.execute(insert_query, (category_id, name, industry_id, product_services,1))
            print(f"Inserted: {category_id} Name: {name}, Industry ID: {industry_id}, Value: {product_services}")

        conn.commit()
        print("Operation completed successfully.")

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {str(e)}")
        raise e

    finally:
        my_cursor.close()
        conn.close()


def get_api_key(key_name: str):
    conn = create_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT api_key FROM ai_machines WHERE name = %s", (key_name,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return result[0]
    else:
        raise ValueError(f"No API key found for {key_name}")

def fetch_prompt(prompt_name):
    conn = create_db_connection()
    cur = conn.cursor()
    query = "SELECT user_prompt, system_prompt FROM trigger_prompts WHERE prompt_name = %s"
    cur.execute(query, (prompt_name,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return list(result) 
    else:
        raise ValueError(f"Prompt not found for prompt_name {prompt_name}")


