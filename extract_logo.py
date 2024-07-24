import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_logo(url):
    try:
        response = requests.get(url)
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, 'html.parser')

        favicon_url = None

        icon_link = soup.find('link', rel=lambda r: r and ('icon' in r or 'shortcut icon' in r))
        if icon_link and icon_link.has_attr('href'):
            favicon_url = icon_link['href']

        if not favicon_url:
            favicon_url = urljoin(url, '/favicon.ico')


        if favicon_url:
            favicon_url = urljoin(url, favicon_url)

            favicon_response = requests.head(favicon_url)
            if favicon_response.status_code != 200:
                favicon_url = None

        return favicon_url

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

website_url = "https://www.amlrightsource.com/"
favicon_url = extract_logo(website_url)

if favicon_url:
    print(f"Favicon URL: {favicon_url}")
else:
    print("Favicon not found.")