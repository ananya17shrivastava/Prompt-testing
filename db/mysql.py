from typing import List
import uuid

import mysql.connector
from mysql.connector import Error

def create_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='impact360'
        )
        if conn.is_connected():
            print("Connection successful!")
            return conn
    except Error as e:
        print(f"Error: {e}")
        return None

def get_industryid(industryname: str) -> str:
    conn = None
    my_cursor = None
    industry_id = None

    try:
        conn = create_db_connection()
        my_cursor = conn.cursor()

        industry = industryname.replace(' ', '_')
        industry_query = "SELECT id FROM industries WHERE name = %s"
        my_cursor.execute(industry_query, (industry,))
        industry_result = my_cursor.fetchone()

        if not industry_result:
            print(f"Industry '{industry}' not found in the database.")
            return None

        industry_id = industry_result[0]

    except Error as e:
        print(f"An error occurred while fetching industry ID: {str(e)}")
        return None

    finally:
        if my_cursor:
            my_cursor.close()
        if conn:
            conn.close()

    return industry_id



def find_industries() -> List[str]:
    conn = None
    my_cursor = None
    industries = []

    try:
        conn = create_db_connection()
        my_cursor = conn.cursor()

        my_cursor.execute("SELECT name FROM industries")
        names = my_cursor.fetchall()

        for name in names:
            data = name[0].replace('_', ' ')
            print(data)
            industries.append(data)

    except Error as e:
        print(f"An error occurred while fetching industries: {str(e)}")

    finally:
        if my_cursor:
            my_cursor.close()
        if conn:
            conn.close()

    return industries


def insert_industry_category(industry_id: str, name: str, product_services: str):
    conn = create_db_connection()
    my_cursor = conn.cursor()

    try:
        check_query = """
            SELECT id FROM industry_categories 
            WHERE industry_id = %s AND name = %s
        """
        my_cursor.execute(check_query, (industry_id, name))
        existing_record = my_cursor.fetchone()

        if existing_record:
            update_query = """
                UPDATE industry_categories 
                SET products_and_services = %s
                WHERE industry_id = %s AND name = %s
            """
            my_cursor.execute(update_query, (product_services, industry_id, name))
            print(f"Updated: Name: {name}, Industry ID: {industry_id}, Value: {product_services}")
        else:
            category_id = str(uuid.uuid4())
            insert_query = """
                INSERT INTO industry_categories 
                (id, name, source_id, industry_id, products_and_services) 
                VALUES (%s, %s, NULL, %s, %s)
            """
            my_cursor.execute(insert_query, (category_id, name, industry_id, product_services))
            print(f"Inserted: ID: {category_id}, Name: {name}, Industry ID: {industry_id}, Value: {product_services}")

        conn.commit()
        print("Operation completed successfully.")

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {str(e)}")

    finally:
        my_cursor.close()
        conn.close()
