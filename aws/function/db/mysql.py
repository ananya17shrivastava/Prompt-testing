from mysql.connector import Error
import mysql.connector
from typing import List, TypedDict
import uuid
import os
from urllib.parse import urlparse


def create_db_connection(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE):
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        connection_timeout=1000,
    )
    if conn.is_connected():
        # print("Connection successful!")
        return conn

def extract_name_from_url(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # Remove 'www.' if present
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Split by '.' and take all parts except the last if there are more than 2 parts
    parts = domain.split('.')
    if len(parts) > 2:
        name = '.'.join(parts[:-1])
    else:
        name = domain
    return name



def feed_response_to_sql(prompt_id: str, ai_machine_id: str, response_data: str,conn):
    my_cursor = None
    try:
        my_cursor = conn.cursor()
        new_id = str(uuid.uuid4())
        sql = "INSERT INTO completions (id, trigger_prompt_id, ai_machine_id, response) VALUES (%s, %s, %s, %s)"
        my_cursor.execute(sql, (new_id, prompt_id, ai_machine_id, response_data))
        print(f"LLM response fed to the database with id {new_id}!")
        conn.commit()
    except Error as e:
        print(f"An error occurred while inserting response: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if my_cursor:
            my_cursor.close()

def insert_industry_category(industry_id: str, name: str, product_services: str,conn):
    # conn = create_db_connection()
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
        # conn.close()

def insert_solutions(case_id: str, name: str, url: str,logo_url:str,is_url_valid, conn):
    my_cursor = None
    try:
        my_cursor = conn.cursor()

        check_query = """
        SELECT id FROM solutions
        WHERE name = %s
        """
        my_cursor.execute(check_query, (name,))
        existing_records = my_cursor.fetchall()

        if not existing_records:
            # Insert new record
            insert_query = """
            INSERT INTO solutions (id, name, created_at, organization_creator_id, documentation_url, ai_generated,logo_url,is_url_valid)
            VALUES (%s, %s, NOW(), %s, %s, %s,%s,%s)
            """
            new_id = str(uuid.uuid4())
            organization_creator_id = 'user_2iNQ8GoBBlyG8NODy4DtUcAIXR2'
            
            
            my_cursor.execute(insert_query, (new_id, name, organization_creator_id, url, 1,logo_url,is_url_valid))

            conn.commit()
            print(f"New solution inserted with id: {new_id}")
            insert_in_case_to_solution(case_id, solution_id=new_id, conn=conn)
        else:
            existing_id = existing_records[0][0]  # Extract the ID from the first tuple in the list
            print(f"Solution already exists by name {name} with id: {existing_id}")
            insert_in_case_to_solution(case_id, solution_id=existing_id, conn=conn)

    except Error as e:
        print(f"An error occurred while inserting solutions: {str(e)}")
        if conn:
            conn.rollback()
        raise

    finally:
        if my_cursor:
            my_cursor.close()

def insert_in_case_to_solution(case_id: str, solution_id: str, conn):
    my_cursor = None
    try:
        my_cursor = conn.cursor()

        check_query = """
        SELECT id FROM case_to_solution
        WHERE case_id = %s AND solution_id = %s
        """
        my_cursor.execute(check_query, (case_id, solution_id))
        existing_records = my_cursor.fetchall()

        if not existing_records:
            insert_query = """
            INSERT INTO case_to_solution (id, case_id, solution_id, created_at)
            VALUES (%s, %s, %s, NOW())
            """
            new_id = str(uuid.uuid4())
            my_cursor.execute(insert_query, (new_id, case_id, solution_id))
            conn.commit()
            print(f"New entry in case_to_solution with id: {new_id}")
        else:
            print(f"Solution already exists for case_id {case_id} and solution_id {solution_id}")

    except Error as e:
        print(f"An error occurred while inserting in case_to_solutions: {str(e)}")
        if conn:
            conn.rollback()
        raise

    finally:
        if my_cursor:
            my_cursor.close()



def insert_business_areas(name: str, description: str, industry_category_id: str, industry_id: str,conn):
    # conn = None
    my_cursor = None
    try:
        # conn = create_db_connection()
        my_cursor = conn.cursor()
        
        check_query = """
        SELECT id FROM business_areas
        WHERE name = %s AND industry_category_id = %s AND industry_id = %s
        """
        my_cursor.execute(check_query, (name, industry_category_id, industry_id))
        existing_record = my_cursor.fetchone()

        if not existing_record:
            # Insert new record
            insert_query = """
            INSERT INTO business_areas (id, name,organization_creator_id, description, industry_category_id, industry_id)
            VALUES (%s, %s,%s, %s, %s, %s)
            """
            new_id = str(uuid.uuid4())
            organization_creator_id='user_2iNQ8GoBBlyG8NODy4DtUcAIXR2'
            my_cursor.execute(insert_query, (new_id, name,organization_creator_id, description, industry_category_id, industry_id))
            conn.commit()
            print(f"New business area inserted with id: {new_id}")
            return new_id
        else:
            print("Business area already exists by name {name} for industry category {industry_category_id} of industry {industry_id}")
            # return existing_record[0]

    except Error as e:
        print(f"An error occurred while inserting business area: {str(e)}")
        if conn:
            conn.rollback()
        raise

    finally:
        if my_cursor:
            my_cursor.close()
        # if conn:
            # conn.close()



def feed_logo_to_db(solution_id: str, url: str, documentation_url: str, conn):
    my_cursor = None
    try:
        my_cursor = conn.cursor()
        
        update_query = """
        UPDATE solutions
        SET logo_url = %s, is_url_valid = 1, documentation_url = %s
        WHERE id = %s
        """
        my_cursor.execute(update_query, (url, documentation_url, solution_id))
        
        conn.commit()
        
        rows_affected = my_cursor.rowcount
        if rows_affected > 0:
            print(f"Successfully updated logo_url, is_url_valid, and documentation_url for solution_id: {solution_id}")
            return True
        else:
            print(f"No solution found with id: {solution_id}")
            return False
    except Exception as e:
        print(f"Error updating logo_url, is_url_valid, and documentation_url: {str(e)}")
        conn.rollback()  
        return False
    finally:
        if my_cursor:
            my_cursor.close()


def insert_tasks(name: str, description: str, urls: list, case_id: str, conn):
    my_cursor = None
    try:
        my_cursor = conn.cursor()

        check_query = """
        SELECT id FROM tasks
        WHERE name = %s AND case_id = %s
        """
        my_cursor.execute(check_query, (name, case_id))
        existing_records = my_cursor.fetchall()

        if not existing_records:

            insert_query = """
            INSERT INTO tasks (id, name, created_at, organization_creator_id, case_id, description)
            VALUES (%s, %s, NOW(), %s, %s, %s)
            """
            new_id = str(uuid.uuid4())
            organization_creator_id = 'user_2iNQ8GoBBlyG8NODy4DtUcAIXR2' 
            my_cursor.execute(insert_query, (new_id, name, organization_creator_id , case_id, description))
            
            if urls:
                url_insert_query = """
                INSERT INTO research_sources (id, case_id, url, task_id)
                VALUES (%s, %s, %s, %s)
                """
                url_data = [(str(uuid.uuid4()), case_id, url, new_id) for url in urls]
                my_cursor.executemany(url_insert_query, url_data)

            conn.commit()
            print(f"New task inserted with id: {new_id}")
            return new_id
        else:
            existing_id = existing_records[0][0] 
            print(f"Task already exists with name '{name}' for case_id {case_id}. Existing task id: {existing_id}")
            return existing_id

    except Error as e:
        print(f"An error occurred while inserting task: {str(e)}")
        if conn:
            conn.rollback()
        raise

    finally:
        if my_cursor:
            my_cursor.close()





def insert_url_kpi(url: str, case_id: str,impact_kpi_id:str,conn):
    try:
        # conn = create_db_connection()
        my_cursor = conn.cursor()
        
        
        id = str(uuid.uuid4())

        query = "INSERT INTO research_sources (id, case_id, url,impact_kpi_id) VALUES (%s, %s, %s, %s)"
        values = (id, case_id, url,impact_kpi_id)

        my_cursor.execute(query, values)
        conn.commit()

        print(f"URL inserted successfully for kpi id {impact_kpi_id}")  

    except Error as e:
        print(f"Error: {e}")

    finally:
        if conn.is_connected(): 
            my_cursor.close()
            # conn.close()

def feed_kpi(solution_id: str, case_id: str, name: str, description: str, effect: str, unit: str, expected_impact: str, urls: List[str], type: str,conn):
    # conn = None
    my_cursor = None
    try:
        # conn = create_db_connection()
        my_cursor = conn.cursor()
        
        check_query = """
        SELECT id FROM impact_kpis
        WHERE case_id = %s AND solution_id = %s AND name = %s
        """
        my_cursor.execute(check_query, (case_id, solution_id, name)) 
        existing_record = my_cursor.fetchone()

        if not existing_record:
            insert_query = """
            INSERT INTO impact_kpis 
            (id, solution_id, case_id, name, effect, unit, organization_creator_id, ai_generated, description, expected_impact, type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            organization_creator_id = 'user_2iNQ8GoBBlyG8NODy4DtUcAIXR2'
            new_id = str(uuid.uuid4())  
            ai_generated = 1  

            data = (new_id, solution_id, case_id, name, effect, unit, organization_creator_id, ai_generated, description, expected_impact, type)
            my_cursor.execute(insert_query, data)
            
            for url in urls:
                insert_url_kpi(url,case_id, impact_kpi_id=new_id,conn=conn)
            
            conn.commit()
            print(f"New KPI inserted with ID: {new_id}")
        else:
            print(f"KPI already exists for case_id {case_id}, solution_id {solution_id}, and name {name}")

    except Error as e:
        print(f"An error occurred while inserting in impact_kpis: {str(e)}")
        if conn:
            conn.rollback()
        raise

    finally:
        if my_cursor:
            my_cursor.close()





def insert_usecase(name:str,description:str,business_area_id:str,industry_category_id:str,industry_id:str,urls: List[str],conn):
    # conn=create_db_connection()
    my_cursor=conn.cursor()
    try:
        check_query = """
            SELECT id FROM cases
            WHERE business_area_id = %s and name = %s
        """
        my_cursor.execute(check_query, (business_area_id, name,))
        existing_record = my_cursor.fetchone()

        if not existing_record:
            # category_id = str(uuid.uuid4())
            insert_query = """
                INSERT INTO cases
                (id, name,industry_id,created_at,organization_creator_id,description,industry_category_id,business_area_id)
                VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s)
            """
            usecase_id = str(uuid.uuid4())
            organization_creator_id='user_2iNQ8GoBBlyG8NODy4DtUcAIXR2'

            my_cursor.execute(insert_query, (usecase_id, name, industry_id,organization_creator_id,description,industry_category_id,business_area_id))
            print(f"Inserted Name: {name}, Industry ID: {industry_id}, Industry_category_id:{industry_category_id}, business_area_id: {business_area_id}")
            for url in urls:
                insert_url(url,usecase_id,conn)

        conn.commit()
        print("Operation completed successfully.")

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {str(e)}")
        raise e

    finally:
        my_cursor.close()
        # conn.close()

def insert_url(url: str, usecase_id: str,conn):
    try:
        # conn = create_db_connection()
        my_cursor = conn.cursor()


        id = str(uuid.uuid4())

        query = "INSERT INTO research_sources (id, case_id, url) VALUES (%s, %s, %s)"
        values = (id, usecase_id, url)

        my_cursor.execute(query, values)
        conn.commit()

        print(f"URL inserted successfully for {usecase_id}")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if conn.is_connected():
            my_cursor.close()
            # conn.close()




def get_api_key(key_name: str,conn):
    cur = conn.cursor()
    cur.execute("SELECT api_key FROM ai_machines WHERE name = %s", (key_name,))
    result = cur.fetchone()
    cur.close()
    # conn.close()
    if result:
        return result[0]
    else:
        raise ValueError(f"No API key found for {key_name}")


