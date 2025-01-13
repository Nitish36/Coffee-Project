import csv
import gspread
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from pytz import timezone
from gspread_dataframe import set_with_dataframe

# List of URLs to fetch data from
urls = [
    "https://ravecoffee.co.uk/products.json", 
    "https://www.coffee-direct.co.uk/products.json",
    "https://bluetokaicoffee.com/products.json",
    "https://www.cworks.co.uk/products.json",
    "https://coffeebeanshop.co.uk/products.json",
    "https://www.origincoffee.co.uk/products.json",
    "https://kotacoffee.com/products.json",
    "https://www.goodlifecoffee.com/products.json",
    "https://workshopcoffee.com/products.json"
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
    product = []
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
    variant = []
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


def write_data():
    # Read the data from CSV files
    product_df = pd.read_csv("dataset/products.csv")
    variant_df = pd.read_csv("dataset/variants.csv")

    # Google Sheets details
    PRODUCT_GSHEET_NAME = 'Coffee Products'
    VARIANT_GSHEET_NAME = 'Coffee Variants'
    PRODUCT_TAB = 'Products'
    VARIANT_TAB = 'Variants'
    credentialsPath = os.path.expanduser("cred/ct-email-generation-fd91c0d8a01e.json")

    if os.path.isfile(credentialsPath):
        # Authenticate with Google Sheets API
        gc = gspread.service_account(filename=credentialsPath)

        # Handle the Products Google Sheet

        product_sh = gc.open(PRODUCT_GSHEET_NAME)
        product_worksheet = product_sh.worksheet(PRODUCT_TAB)
        product_worksheet.clear()  # Clear existing data

        set_with_dataframe(product_worksheet, product_df)

        # Handle the Variants Google Sheet

        variant_sh = gc.open(VARIANT_GSHEET_NAME)
        variant_worksheet = variant_sh.worksheet(VARIANT_TAB)
        variant_worksheet.clear()  # Clear existing data
        set_with_dataframe(variant_worksheet, variant_df)

        print("Data has been written to separate Google Sheets successfully!")
    else:
        print(f"Credentials file not found at {credentialsPath}")


# Loop through each URL and fetch data, then save the results to CSV files
for url in urls:
    data = fetch_data(url)
    
    # Save product and variant data for each URL into separate files
    save_product_data(data["products"], "dataset/products.csv")
    save_variant_data(data["products"], "dataset/variants.csv")


def write_data2():
    # Read the data from CSV files
    product_df = pd.read_csv("dataset/products.csv")
    variant_df = pd.read_csv("dataset/variants.csv")

    # Define the IST timezone
    ist_timezone = timezone('Asia/Kolkata')

    # Convert datetime columns for product_df
    for col in ['published_at', 'created_at', 'updated_at']:
        if col in product_df.columns:
            # Convert to datetime, handle invalid values, and set UTC
            product_df[col] = pd.to_datetime(product_df[col], errors='coerce', utc=True)
            # Convert to IST
            product_df[col] = product_df[col].dt.tz_convert(ist_timezone)

    # Add a Date_Recorded column for product_df
    if 'created_at' in product_df.columns:
        product_df['Date_Recorded'] = product_df['created_at'].dt.date

    # Convert datetime columns for variant_df
    for col in ['created_at', 'updated_at']:
        if col in variant_df.columns:
            variant_df[col] = pd.to_datetime(variant_df[col], errors='coerce', utc=True)
            variant_df[col] = variant_df[col].dt.tz_convert(ist_timezone)

    # Add a Date_Recorded column for variant_df
    if 'created_at' in variant_df.columns:
        variant_df['Date_Recorded'] = variant_df['created_at'].dt.date

    # Google Sheets details
    PRODUCT_GSHEET_NAME = 'Coffee Products'
    VARIANT_GSHEET_NAME = 'Coffee Variants'
    PRODUCT_TAB = 'Products'
    VARIANT_TAB = 'Variants'
    credentialsPath = os.path.expanduser("credentials/diamond-analysis-ac6758ca1ace.json")

    if os.path.isfile(credentialsPath):
        # Authenticate with Google Sheets API
        gc = gspread.service_account(filename=credentialsPath)

        # Handle the Products Google Sheet
        product_sh = gc.open(PRODUCT_GSHEET_NAME)
        product_worksheet = product_sh.worksheet(PRODUCT_TAB)
        product_worksheet.clear()  # Clear existing data
        set_with_dataframe(product_worksheet, product_df)

        # Handle the Variants Google Sheet
        variant_sh = gc.open(VARIANT_GSHEET_NAME)
        variant_worksheet = variant_sh.worksheet(VARIANT_TAB)
        variant_worksheet.clear()  # Clear existing data
        set_with_dataframe(variant_worksheet, variant_df)

        print("Data has been written to separate Google Sheets successfully!")
    else:
        print(f"Credentials file not found at {credentialsPath}")


# Loop through each URL and fetch data, then save the results to CSV files
for url in urls:
    data = fetch_data(url)

    # Save product and variant data for each URL into separate files
    save_product_data(data["products"], "dataset/products.csv")
    save_variant_data(data["products"], "dataset/variants.csv")



print("Data has been saved to 'products.csv' and 'variants.csv'.")
write_data()
write_data2()