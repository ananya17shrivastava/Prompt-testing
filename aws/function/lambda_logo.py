from botocore.exceptions import ClientError
import logging
import boto3
import jsonpickle
import time
from typing import List
import json
import os
from db.mysql import  create_db_connection,feed_logo_to_db
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import tldextract


logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('lambda')


def get_secret():

    secret_name = "llmapp"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # print(get_secret_value_response)
    secret = get_secret_value_response['SecretString']
    secretJSON = json.loads(secret)
    return secretJSON


secrets = get_secret()


logger = logging.getLogger(__name__)

def is_valid_image_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.head(url, timeout=300, allow_redirects=True, headers=headers)
        content_type = response.headers.get('Content-Type', '')
        return response.status_code == 200 and content_type.startswith('image/')
    except requests.RequestException:
        return False
    

def extract_logo(documentation_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(documentation_url, timeout=300, headers=headers)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        possible_locations = [
            ('link', {'rel': ['icon', 'shortcut icon', 'apple-touch-icon']}),
            ('meta', {'name': 'msapplication-TileImage'}),
            ('meta', {'property': 'og:image'}),
            ('img', {'class': lambda x: x and ('logo' in x.lower())}),
            ('img', {'alt': lambda x: x and 'logo' in x.lower()}),
            ('svg', {'class': lambda x: x and ('logo' in x.lower())}),
        ]

        for tag, attrs in possible_locations:
            if tag == 'link' and 'rel' in attrs:
                elements = soup.find_all(tag, rel=attrs['rel'])
            else:
                elements = soup.find_all(tag, attrs)
            
            for element in elements:
                favicon_url = element.get('href') or element.get('content') or element.get('src')
                if favicon_url:
                    full_favicon_url = urljoin(documentation_url, favicon_url)
                    if is_valid_image_url(full_favicon_url):
                        return full_favicon_url

        default_favicon_url = urljoin(documentation_url, '/favicon.ico')
        if is_valid_image_url(default_favicon_url):
            return default_favicon_url

        all_images = soup.find_all('img', src=True)
        for img in all_images:
            src = img['src']
            if 'logo' in src.lower():
                full_img_url = urljoin(documentation_url, src)
                if is_valid_image_url(full_img_url):
                    return full_img_url

        elements_with_style = soup.find_all(style=True)
        for element in elements_with_style:
            style = element['style']
            if 'logo' in style.lower():
                match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                if match:
                    logo_url = match.group(1)
                    full_logo_url = urljoin(documentation_url, logo_url)
                    if is_valid_image_url(full_logo_url):
                        return full_logo_url

        header = soup.find(['header', 'nav'])
        if header:
            header_images = header.find_all('img', src=True)
            for img in header_images:
                full_img_url = urljoin(documentation_url, img['src'])
                if is_valid_image_url(full_img_url):
                    return full_img_url

        svg_logos = soup.find_all('svg')
        for svg in svg_logos:
            if 'logo' in str(svg).lower():
                
                return f"data:image/svg+xml,{svg}"

        css_links = soup.find_all('link', rel='stylesheet')
        for css_link in css_links:
            css_url = urljoin(documentation_url, css_link['href'])
            css_response = requests.get(css_url, timeout=300)
            if css_response.status_code == 200:
                logo_matches = re.findall(r'url\(["\']?([^"\']+logo[^"\']+)["\']?\)', css_response.text, re.IGNORECASE)
                for match in logo_matches:
                    full_logo_url = urljoin(css_url, match)
                    if is_valid_image_url(full_logo_url):
                        return full_logo_url

        logger.warning(f"No suitable logo found for {documentation_url}")
        return None

    except requests.RequestException as e:
        logger.error(f"An error occurred while extracting logo from {documentation_url}: {e}")
        return None

    
def check_db_solutions_logo(solution_id: str, conn):
    my_cursor = None
    try:
        my_cursor = conn.cursor()
        check_query = "SELECT logo_url FROM solutions WHERE id = %s AND logo_url IS NOT NULL"
        my_cursor.execute(check_query, (solution_id,))
        existing_records = my_cursor.fetchall()
        return len(existing_records) > 0
    finally:
        if my_cursor:
            my_cursor.close()

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info(f"Event: {event}")

    conn = create_db_connection(secrets["MYSQL_HOST"], secrets["MYSQL_USER"], secrets['MYSQL_PASSWORD'], secrets["MYSQL_DATABASE"])
    
    try:
        for record in event['Records']:
            start_time_whole = time.time()
            
            message_body = json.loads(record['body'])
            message_type = message_body.get('type', '').lower()

            if 'logo' not in message_type:
                logger.info("Not related to logo lambda function!")
                continue

            solution_id = message_body.get('solution_id', 'N/A')
            complete_url = message_body.get('documentation_url', 'N/A')

            if check_db_solutions_logo(solution_id, conn):
                logger.info(f"Logo for solution {solution_id} already exists!")
                continue

            extracted = tldextract.extract(complete_url)
            domain = f"{extracted.domain}.{extracted.suffix}"                
            documentation_url=f"https://{domain}"
            # print("COMPLETE URL IS ::::")
            # print(complete_url)
            # print("DOCUMENTATION URL IS ::::")
            # print(documentation_url)
            url = extract_logo(documentation_url)

            if url:
                feed_logo_to_db(solution_id, url,documentation_url, conn)
            else:
                logger.warning(f"No logo found for solution {solution_id}")

            logger.info(f"Time for ONE ITERATION: {time.time() - start_time_whole}")
    finally:
        if conn:
            conn.close()

    return {'statusCode': 200}