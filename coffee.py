import gspread
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from gspread_dataframe import set_with_dataframe
import json
import os
import pandas as pd

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

# Function to create product data (dictionary) for Google Sheets upload
def create_product_data(products):
    product_data = []
    for product_item in products:
        cleaned_body_html = clean_html(product_item["body_html"])
        date_recorded = datetime.fromisoformat(product_item["created_at"]).date()

        product_data.append({
            "id": product_item["id"],
            "title": product_item["title"],
            "handle": product_item["handle"],
            "body_html": cleaned_body_html,
            "published_at": product_item["published_at"],
            "created_at": product_item["created_at"],
            "updated_at": product_item["updated_at"],
            "vendor": product_item["vendor"],
            "product_type": product_item["product_type"],
            "tags": ', '.join(product_item["tags"]),
            "Date_Recorded": date_recorded
        })
    return product_data

# Function to create variant data (dictionary) for Google Sheets upload
def create_variant_data(products):
    variant_data = []
    for product_item in products:
        for variant_item in product_item["variants"]:
            date_recorded = datetime.fromisoformat(variant_item["created_at"]).date()

            variant_data.append({
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
                "Date_Recorded": date_recorded
            })
    return variant_data

# Function to upload product and variant data to Google Sheets (personal ID)
# Correct range calculation for batch_clear
def write_data2():
    # Google Sheets details
    PRODUCT_GSHEET_NAME = 'Coffee Products'
    VARIANT_GSHEET_NAME = 'Coffee Variants'
    PRODUCT_TAB = 'Products'
    VARIANT_TAB = 'Variants'

    # Authenticate with Google Sheets API
    gsheet_credentials = json.loads(os.getenv("GSHEET_TOKEN"))
    gc = gspread.service_account_from_dict(gsheet_credentials)

    # Create product data and variant data
    product_data = []
    variant_data = []

    # Loop through each URL and fetch data
    for url in urls:
        data = fetch_data(url)
        product_data.extend(create_product_data(data["products"]))
        variant_data.extend(create_variant_data(data["products"]))

    # Handle the Products Google Sheet
    product_sh = gc.open(PRODUCT_GSHEET_NAME)
    product_worksheet = product_sh.worksheet(PRODUCT_TAB)

    # Check if headers already exist and skip overwriting them
    if not product_worksheet.row_values(1):  # Check if the first row is empty (i.e., no headers)
        product_worksheet.append_row(["id", "title", "handle", "body_html", "published_at", "created_at", "updated_at", "vendor", "product_type", "tags", "Date_Recorded"])

    # Calculate the last row and column
    num_rows = len(product_data) + 1  # +1 for header row
    num_cols = len(product_data[0])  # Number of columns based on the first data row
    last_cell = f"{chr(64 + num_cols)}{num_rows}"  # Construct the last cell (e.g., 'D271')

    # Clear the data (from row 2 onwards)
    product_worksheet.batch_clear([f"A2:{last_cell}"])
    set_with_dataframe(product_worksheet, pd.DataFrame(product_data))

    # Handle the Variants Google Sheet
    variant_sh = gc.open(VARIANT_GSHEET_NAME)
    variant_worksheet = variant_sh.worksheet(VARIANT_TAB)

    # Check if headers already exist and skip overwriting them
    if not variant_worksheet.row_values(1):  # Check if the first row is empty (i.e., no headers)
        variant_worksheet.append_row(["id", "title", "option1", "option2", "option3", "sku", "requires_shipping", "taxable", "featured_image_src", "available", "price", "grams", "compare_at_price", "position", "product_id", "created_at", "updated_at", "Date_Recorded"])

    # Calculate the last row and column for variants
    num_rows_variant = len(variant_data) + 1  # +1 for header row
    num_cols_variant = len(variant_data[0])  # Number of columns based on the first data row
    last_cell_variant = f"{chr(64 + num_cols_variant)}{num_rows_variant}"  # Construct the last cell (e.g., 'P350')

    # Clear the data (from row 2 onwards)
    variant_worksheet.batch_clear([f"A2:{last_cell_variant}"])
    set_with_dataframe(variant_worksheet, pd.DataFrame(variant_data))

    print("Data has been written to Google Sheets successfully!")

# Call the function to upload data to Google Sheets
write_data2()


# Call the function to upload data to Google Sheets
write_data2()
