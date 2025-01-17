import csv
import gspread
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from pytz import timezone
from gspread_dataframe import set_with_dataframe
import json
from datetime import datetime

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
    product_headers = ["id", "title", "handle", "body_html", "published_at", "created_at", "updated_at", "vendor", "product_type", "tags", "Date_Recorded"]
    product = []
    with open(filename, mode='a', newline='', encoding='utf-8') as file:  # Open in append mode
        writer = csv.DictWriter(file, fieldnames=product_headers)

        # If the file is empty, write the header
        if file.tell() == 0:
            writer.writeheader()

        for product_item in products:
            # Clean the body_html to remove HTML tags and retain only the text
            cleaned_body_html = clean_html(product_item["body_html"])

            # Extract date from created_at (assuming it's in ISO 8601 format)
            date_recorded = datetime.fromisoformat(product_item["created_at"]).date()

            product_data = {
                "id": product_item["id"],
                "title": product_item["title"],
                "handle": product_item["handle"],
                "body_html": cleaned_body_html,  # Updated to contain cleaned text
                "published_at": product_item["published_at"],
                "created_at": product_item["created_at"],
                "updated_at": product_item["updated_at"],
                "vendor": product_item["vendor"],
                "product_type": product_item["product_type"],
                "tags": ', '.join(product_item["tags"]),  # Convert tags list to a comma-separated string
                "Date_Recorded": date_recorded  # Added Date_Recorded column
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

        for product_item in products:
            for variant_item in product_item["variants"]:
                # Extract date from created_at (assuming it's in ISO 8601 format)
                date_recorded = datetime.fromisoformat(variant_item["created_at"]).date()

                variant_data = {
                    "id": variant_item["id"],
                    "title": variant_item["title"],
                    "option1": variant_item["option1"],
                    "option2": variant_item["option2"],
                    "option3": variant_item["option3"],
                    "sku": variant_item["sku"],
                    "requires_shipping": variant_item["requires_shipping"],
                    "taxable": variant_item["taxable"],
                    "featured_image_src": variant_item["featured_image"]["src"] if variant_item.get("featured_image") else None,
                    "available": variant_item["available"],
                    "price": variant_item["price"],
                    "grams": variant_item["grams"],
                    "compare_at_price": variant_item["compare_at_price"],
                    "position": variant_item["position"],
                    "product_id": variant_item["product_id"],
                    "created_at": variant_item["created_at"],
                    "updated_at": variant_item["updated_at"],
                    "Date_Recorded": date_recorded  # Added Date_Recorded column
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

    # Load credentials from the GSHEET_TOKEN environment variable
    gsheet_credentials = json.loads(os.getenv("GSHEET_TOKEN"))
    gc = gspread.service_account_from_dict(gsheet_credentials)

    # Google Sheets details
    PRODUCT_GSHEET_NAME = 'Coffee Products'
    VARIANT_GSHEET_NAME = 'Coffee Variants'
    PRODUCT_TAB = 'Products'
    VARIANT_TAB = 'Variants'

    # Handle the Products Google Sheet
    product_sh = gc.open(PRODUCT_GSHEET_NAME)
    product_worksheet = product_sh.worksheet(PRODUCT_TAB)

    # Check if headers already exist and skip overwriting them
    if not product_worksheet.row_values(1):  # Check if the first row is empty (i.e., no headers)
        set_with_dataframe(product_worksheet, product_df.iloc[0:0])  # Add headers only

    # Clear the data (from row 2 onwards)
    product_worksheet.batch_clear([f"A2:{chr(64+len(product_df.columns))}{len(product_df)+1}"])
    set_with_dataframe(product_worksheet, product_df)

    # Handle the Variants Google Sheet
    variant_sh = gc.open(VARIANT_GSHEET_NAME)
    variant_worksheet = variant_sh.worksheet(VARIANT_TAB)

    # Check if headers already exist and skip overwriting them
    if not variant_worksheet.row_values(1):  # Check if the first row is empty (i.e., no headers)
        set_with_dataframe(variant_worksheet, variant_df.iloc[0:0])  # Add headers only

    # Clear the data (from row 2 onwards)
    variant_worksheet.batch_clear([f"A2:{chr(64+len(variant_df.columns))}{len(variant_df)+1}"])
    set_with_dataframe(variant_worksheet, variant_df)

    print("Data has been written to separate Google Sheets successfully!")

# Loop through each URL and fetch data, then save the results to CSV files
for url in urls:
    data = fetch_data(url)

    # Save product and variant data for each URL into separate files
    save_product_data(data["products"], "dataset/products.csv")
    save_variant_data(data["products"], "dataset/variants.csv")

print("Data has been saved to 'products.csv' and 'variants.csv'.")
write_data2()
