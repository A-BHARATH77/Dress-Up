import requests
from bs4 import BeautifulSoup
import sys
import json
from detect_dress import get_dress_type

sys.stdout.reconfigure(encoding='utf-8')

def get_amazon_results(color, dress_type):
    search_query = f"{color}+{dress_type}".replace(" ", "+")
    
    payload = {
    'api_key': 'bef907963d52f5afde039299486a1554',  # Your ScraperAPI key
        'url': f'https://www.amazon.in/s?k={search_query}',  
        'country_code': 'in',
        'device_type': 'mobile'
    }

    response = requests.get('https://api.scraperapi.com/', params=payload)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})

        results = []
        for product in product_containers[:5]:  # Get top 5 results
            title_tag = product.find('span', {'class': 'a-text-normal'})
            price_tag = product.find('span', {'class': 'a-price-whole'})
            link_tag = product.find('a', {'class': 'a-link-normal'})

            product_name = title_tag.get_text() if title_tag else 'No title'
            product_price = price_tag.get_text() if price_tag else 'Price not available'
            product_url = 'https://www.amazon.in' + link_tag.get('href') if link_tag else 'No link'

            results.append({
                "name": product_name,
                "price": f"₹{product_price}",
                "url": product_url
            })

        return json.dumps({"products": results})
    else:
        return json.dumps({"error": "Error fetching the page."})

if __name__ == "__main__":
    color = sys.argv[1]
    dress_type = sys.argv[2]
    print(get_amazon_results(color, dress_type))
