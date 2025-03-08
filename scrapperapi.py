import requests
from bs4 import BeautifulSoup
import sys
sys.stdout.reconfigure(encoding='utf-8')
from detect_dress import get_dress_type

# Get user input for color and type of dress
dress_type = get_dress_type()
print("Dress type:", dress_type)
color = input("Enter the color of the dress: ")
#dress_type = input("Enter the type of dress: ")

# Construct the search URL based on user input
search_query = f"{color}+{dress_type}".replace(" ", "+")  # Replace spaces with '+' for the URL

# ScraperAPI parameters
payload = {
    'api_key': 'bef907963d52f5afde039299486a1554',  # Your ScraperAPI key
    'url': f'https://www.amazon.in/s?k={search_query}',  # URL for the search
    'country_code': 'in',  # Country code for India (Amazon.in)
    'device_type': 'mobile'  # Use 'desktop' for desktop view, 'mobile' for mobile view
}

# Send GET request to ScraperAPI
response = requests.get('https://api.scraperapi.com/', params=payload)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'lxml')

    # Find product containers (adjust the selector based on Amazon's structure)
    product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})

    # Process only the first product
    if product_containers:
        product = product_containers[0]  # Get the first product container

        # Get product title
        title_tag = product.find('span', {'class': 'a-text-normal'})
        product_name = title_tag.get_text() if title_tag else 'No title'

        # Get product price
        price_tag = product.find('span', {'class': 'a-price-whole'})
        product_price = price_tag.get_text() if price_tag else 'Price not available'

        # Get product link
        link_tag = product.find('a', {'class': 'a-link-normal'})
        product_url = 'https://www.amazon.in' + link_tag.get('href') if link_tag else 'No link'

        # Print product details
        print(f"Product: {search_query}")
        print(f"Price: ₹{product_price}")
        print(f"Link: {product_url}")
    else:
        print("No products found.")
else:
    print("Error fetching the page.")