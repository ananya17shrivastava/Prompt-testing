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
    




def feed_response_to_sql(prompt_id: str, name: str, url: str):
    conn = None
    my_cursor = None
    try:
        conn = create_db_connection()
        my_cursor = conn.cursor()

    except Error as e:
        print(f"An error occurred while inserting response: {str(e)}")
        if conn:
            conn.rollback()
        raise

    finally:
        if my_cursor:
            my_cursor.close()
        if conn:
            conn.close()
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
                s.ai_generated = 1 AND s.id='006ef88b-15a2-4ea3-9348-09b5dc30396d';
        """

        my_cursor.execute(query)
        results = my_cursor.fetchall()

        for row in results:
            ai_solutions.append({
                "solution_id": row['solution_id'],
                "solution_name": row['solution_name'].replace('_', ' '),
                "usecase_name": row['usecase_name'].replace('_', ' '),
                "usecase_description": row['usecase_description'],
                "industry_category_name": row['industry_category_name'].replace('_', ' '),
                "industry_name": row['industry_name'].replace('_', ' '),
                "case_id": row['case_id']  
            })

    except Error as e:
        print(f"An error occurred while fetching AI solutions: {str(e)}")
        raise

    finally:
        if my_cursor:
            my_cursor.close()
        if conn:
            conn.close()

    return ai_solutions

    

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
                c.id='00010fdf-26d0-4953-bcba-3044faf2b770'
            ORDER BY 
                i.name, ic.name, c.name;
        """

        my_cursor.execute(query)
        results = my_cursor.fetchall()
        print(results)

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

def insert_solutions(case_id: str, name: str, url: str):
    conn = None
    my_cursor = None
    try:
        conn = create_db_connection()
        my_cursor = conn.cursor()
        
        check_query = """
        SELECT id FROM solutions
        WHERE name = %s 
        """
        my_cursor.execute(check_query, (name,)) 
        existing_record = my_cursor.fetchone()

        if not existing_record:
            # Insert new record
            insert_query = """
            INSERT INTO solutions (id, name, created_at, organization_creator_id, documentation_url, ai_generated)
            VALUES (%s, %s, NOW(), %s, %s, %s)
            """
            new_id = str(uuid.uuid4())
            organization_creator_id = 'user_2iNQ8GoBBlyG8NODy4DtUcAIXR2'
            my_cursor.execute(insert_query, (new_id, name, organization_creator_id, url, 1))
            conn.commit()
            print(f"New solution inserted with id: {new_id}")
            insert_in_case_to_solution(case_id, solution_id=new_id)
        else:
            existing_id = existing_record[0] 
            print(f"Solution already exists by name {name} with id: {existing_id}")
            insert_in_case_to_solution(case_id, solution_id=existing_id)

    except Error as e:
        print(f"An error occurred while inserting solutions: {str(e)}")
        if conn:
            conn.rollback()
        raise

    finally:
        if my_cursor:
            my_cursor.close()
        if conn:
            conn.close()

def insert_in_case_to_solution(case_id: str, solution_id: str):
    conn = None
    my_cursor = None
    try:
        conn = create_db_connection()
        my_cursor = conn.cursor()
        
        check_query = """
        SELECT id FROM case_to_solution
        WHERE case_id = %s AND solution_id = %s
        """
        my_cursor.execute(check_query, (case_id, solution_id))  # Changed new_id to solution_id
        existing_record = my_cursor.fetchall()

        if not existing_record:
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
        if conn:
            conn.close()

def insert_url_kpi(url: str, case_id: str,impact_kpi_id:str):
    try:
        conn = create_db_connection()
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
            conn.close()

def feed_kpi(solution_id: str, case_id: str, name: str, description: str, effect: str, unit: str, expected_impact: str, urls: List[str], type: str):
    conn = None
    my_cursor = None
    try:
        conn = create_db_connection()
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
                insert_url_kpi(url,case_id, impact_kpi_id=new_id)
            
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
        if conn:
            conn.close()


class Industry_Category(TypedDict):
    category_name: str
    industry_name: str
    industry_id: str
    industry_category_id: str

def find_industry_categories() -> List[Industry_Category]:
    conn = None
    my_cursor = None
    industry_categories: List[Industry_Category] = []

    try:
        conn = create_db_connection()
        my_cursor = conn.cursor()
        query = """
            SELECT 
                ic.name AS category_name,
                i.name AS industry_name,
                ic.industry_id,
                ic.id AS industry_category_id
            FROM 
                industry_categories ic
            JOIN 
                industries i ON ic.industry_id = i.id
            WHERE 
                i.id != 'be4f80ec-3678-4bf2-b6b6-f5e69301a95c'
            """

        my_cursor.execute(query)

        results = my_cursor.fetchall()

        for category_name, industry_name, industry_id, industry_category_id in results:
            category_name = category_name.replace('_', ' ')
            industry_name = industry_name.replace('_', ' ')
            industry_categories.append({
                "category_name": category_name,
                "industry_name": industry_name,
                "industry_id": industry_id,
                "industry_category_id": industry_category_id
            })

    except Error as e:
        print(f"An error occurred while fetching industry_categories: {str(e)}")
        raise

    finally:
        if my_cursor:
            my_cursor.close()
        if conn:
            conn.close()

    return industry_categories


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

def insert_business_areas(name: str, description: str, industry_category_id: str, industry_id: str):
    conn = None
    my_cursor = None
    try:
        conn = create_db_connection()
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
        if conn:
            conn.close()

def insert_industry_business_areas(name: str, description: str, industry_id: str):
    conn = None
    my_cursor = None
    try:
        conn = create_db_connection()
        my_cursor = conn.cursor()
        
        # check_query = """
        # SELECT id FROM business_areas
        # WHERE name = %s AND industry_id = %s
        # """
        # my_cursor.execute(check_query, (name, industry_id))
        # existing_record = my_cursor.fetchone()

        # if not existing_record:
            # Insert new record
        insert_query = """
        INSERT INTO business_areas (id, name,organization_creator_id, description, industry_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        new_id = str(uuid.uuid4())
        organization_creator_id='user_2iNQ8GoBBlyG8NODy4DtUcAIXR2'
        my_cursor.execute(insert_query, (new_id, name,organization_creator_id, description, industry_id))
        conn.commit()
        print(f"New business area inserted with id: {new_id}")
        return new_id
    # else:
    #     print("Business area already exists by name {name} for the industry {industry_id}")
    #     # return existing_record[0]

    except Error as e:
        print(f"An error occurred while inserting business area: {str(e)}")
        if conn:
            conn.rollback()
        raise

    finally:
        if my_cursor:
            my_cursor.close()
        if conn:
            conn.close()


def insert_usecase(name:str,description:str,business_area_id:str,industry_category_id:str,industry_id:str,urls: List[str]):
    conn=create_db_connection()
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
                insert_url(url,usecase_id)

        conn.commit()
        print("Operation completed successfully.")

    except Exception as e:
        conn.rollback()
        print(f"An error occurred: {str(e)}")
        raise e

    finally:
        my_cursor.close()
        conn.close()

def insert_url(url: str, usecase_id: str):
    try:
        conn = create_db_connection()
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
            conn.close()



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



# from langfuse import Langfuse

# langfuse = Langfuse(
#   secret_key="sk-lf-bd87adfb-1b98-41c3-8952-700e09b521df",
#   public_key="pk-lf-f630c131-97e4-46af-b68d-efe27548c910",
#   host="https://cloud.langfuse.com"
# )

class Prompt(TypedDict):
    user_prompt: str
    system_prompt: str

def fetch_prompt(prompt_name: str) -> Prompt:
    conn = create_db_connection()
    cur = conn.cursor()
    
    query = "SELECT user_prompt, system_prompt FROM trigger_prompts WHERE prompt_name = %s"
    cur.execute(query, (prompt_name,))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return Prompt(user_prompt=result[0], system_prompt=result[1])
    else:
        raise ValueError(f"Prompt not found for prompt_name {prompt_name}")



# class Prompt(TypedDict):
#     user_prompt: str
#     system_prompt: str

# def fetch_prompt(prompt_name: str) -> List[Prompt]:
#     prompts: List[Prompt] = []
#     conn = None
#     cur = None

#     try:
#         conn = create_db_connection()
#         cur = conn.cursor()
    
#         query = """
#         SELECT user_prompt, system_prompt 
#         FROM trigger_prompts
#         WHERE prompt_name = %s
#         """

#         cur.execute(query, (prompt_name,))

#         results = cur.fetchall()
#         print(f"Fetched results: {results}")

#         for user_prompt, system_prompt in results:
#             prompts.append({
#                 "user_prompt": user_prompt,
#                 "system_prompt": system_prompt
#             })

#         print(f"Processed prompts: {prompts}")

#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         raise

#     finally:
#         if cur:
#             cur.close()
#         if conn:
#             conn.close()

#     return prompts