import csv
import requests
from bs4 import BeautifulSoup

# List of URLs to fetch data from
urls = [
    "https://ravecoffee.co.uk/products.json", 
    "https://www.coffee-direct.co.uk/products.json",
    "https://bluetokaicoffee.com/products.json",
    "https://www.cworks.co.uk/products.json",
    "https://coffeebeanshop.co.uk/products.json"
]

# Function to fetch data from a URL
def fetch_data(url):
    response = requests.get(url)
    return response.json()

# Function to clean HTML and extract only the text content
def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(strip=True)

# Function to save product data into a CSV file
def save_product_data(products, filename):
    product_headers = ["id", "title", "handle", "body_html", "published_at", "created_at", "updated_at", "vendor", "product_type", "tags"]

    with open(filename, mode='a', newline='', encoding='utf-8') as file:  # Open in append mode
        writer = csv.DictWriter(file, fieldnames=product_headers)

        # If the file is empty, write the header
        if file.tell() == 0:
            writer.writeheader()

        for product in products:
            # Clean the body_html to remove HTML tags and retain only the text
            cleaned_body_html = clean_html(product["body_html"])

            product_data = {
                "id": product["id"],
                "title": product["title"],
                "handle": product["handle"],
                "body_html": cleaned_body_html,  # Updated to contain cleaned text
                "published_at": product["published_at"],
                "created_at": product["created_at"],
                "updated_at": product["updated_at"],
                "vendor": product["vendor"],
                "product_type": product["product_type"],
                "tags": ', '.join(product["tags"])  # Convert tags list to a comma-separated string
            }
            writer.writerow(product_data)

# Function to save variant data into a CSV file
def save_variant_data(products, filename):
    variant_headers = ["id", "title", "option1", "option2", "option3", "sku", "requires_shipping", "taxable", "featured_image_src", "available", "price", "grams", "compare_at_price", "position", "product_id", "created_at", "updated_at"]

    with open(filename, mode='a', newline='', encoding='utf-8') as file:  # Open in append mode
        writer = csv.DictWriter(file, fieldnames=variant_headers)

        # If the file is empty, write the header
        if file.tell() == 0:
            writer.writeheader()

        for product in products:
            for variant in product["variants"]:
                variant_data = {
                    "id": variant["id"],
                    "title": variant["title"],
                    "option1": variant["option1"],
                    "option2": variant["option2"],
                    "option3": variant["option3"],
                    "sku": variant["sku"],
                    "requires_shipping": variant["requires_shipping"],
                    "taxable": variant["taxable"],
                    "featured_image_src": variant["featured_image"]["src"] if variant.get("featured_image") else None,
                    "available": variant["available"],
                    "price": variant["price"],
                    "grams": variant["grams"],
                    "compare_at_price": variant["compare_at_price"],
                    "position": variant["position"],
                    "product_id": variant["product_id"],
                    "created_at": variant["created_at"],
                    "updated_at": variant["updated_at"]
                }
                writer.writerow(variant_data)

# Loop through each URL and fetch data, then save the results to CSV files
for url in urls:
    data = fetch_data(url)
    
    # Save product and variant data for each URL into separate files
    save_product_data(data["products"], "dataset/products.csv")
    save_variant_data(data["products"], "dataset/variants.csv")

print("Data has been saved to 'products.csv' and 'variants.csv'.")
