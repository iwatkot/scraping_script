import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime

# Initial URL address.
init_url = 'https://scrapingclub.com/exercise/list_basic/?page=1'
# Generating clean URL and URL prefix for URL converts.
clean_url = init_url[:init_url.index('?')]
url_prefix = init_url[:init_url.index('/e')]
response = requests.get(init_url)
soup = BeautifulSoup(response.text, 'lxml')
# Extracting pagination information (pages and links).
pages = soup.find('ul', class_='pagination')
links = pages.find_all('a', class_='page-link')
# Preparing list of urls (page1 added manually).
page_urls = ['?page=1']
# Generating list of page URLs.
for link in links:
    if link.text.isdigit():
        page_urls.append(link['href'])
# Preparing list for content.
content = []
# The main cycle starting with page URLs.
for page_url in page_urls:
    # Generating absolute path to the current page.
    url = clean_url + page_url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    # Extracting information about target items.
    items = soup.find_all('div', class_="col-lg-4 col-md-6 mb-4")
    for item in items:
        # Preparing empty dict for each item.
        ic = {}
        item_name = item.find('h4', class_='card-title').text.strip()
        item_full_price = item.find('h5').text
        item_price = item_full_price[1:]
        item_currency = item_full_price[0]
        item_image = url_prefix + item.find('img')['src']
        item_url = url_prefix + item.find('a')['href']
        # Requesting data from item URL.
        inner_response = requests.get(item_url)
        inner_soup = BeautifulSoup(inner_response.text, 'lxml')
        # Extracting item's description from its own page.
        item_description = inner_soup.find('p', class_='card-text').text
        ic['name'] = str(item_name)
        ic['description'] = str(item_description)
        ic['currency'] = str(item_currency)
        ic['price'] = float(item_price)
        ic['image'] = str(item_image)
        ic['url'] = str(item_url)
        # Adding copy of the dict with items to the main content list.
        content.append(ic.copy())
        # Cleaning the dict for next item.
        ic.clear()
# Preparing metadata for JSON file.
now = datetime.now()
current_date = now.strftime("%Y-%m-%d")
current_time = now.strftime("%H-%M")
items_number = len(content)
metadata = {
    'date': current_date,
    'time': current_time,
    'number of items': items_number,
}
# Preparing result dict for packing it into JSON.
data = {
    'metadata': metadata,
    'content': content,
}
# Result filename will containt timestamp.
result_file = f'results_{current_date}_{current_time}.json'
with open(result_file, 'w') as f:
    json.dump(data, f, indent=2)
