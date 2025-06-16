"""
Setup Instructions:
1. pip install playwright python-dotenv requests
2. playwright install
3. playwright codegen target.com (log in and save storage_state.json)
"""

import json
import os
import time
from datetime import datetime
from cart_adders.target import add_to_cart_target
from webhook import send_pushcut_notification


PRODUCTS_FILE = 'products.json'
STORAGE_STATE = 'storage_state.json'

# Helper for timestamped logging
def log(product_name, status):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{product_name}] STATUS: {status}")

def main():
    # Check for storage_state.json
    if not os.path.exists(STORAGE_STATE):
        raise FileNotFoundError(
            f"storage_state.json not found! Please run: playwright codegen target.com and log in."
        )
    # Load products
    try:
        with open(PRODUCTS_FILE, 'r') as f:
            products = json.load(f)
    except Exception as e:
        print(f"Error loading {PRODUCTS_FILE}: {e}")
        return
    for product in products:
        name = product.get('name', 'Unknown')
        url = product.get('url')
        if not url:
            log(name, "Missing URL, skipping.")
            continue
        log(name, f"Checking stock at {url}")
        try:
            added = add_to_cart_target(url, name, STORAGE_STATE)
            if added:
                log(name, "IN STOCK! Added to cart.")

                send_pushcut_notification(
                    message=f"{name} IS IN STOCK!",
                    deep_link="https://www.target.com/cart"
                )

            else:
                log(name, "OUT OF STOCK or Add to Cart not clickable.")
        except Exception as e:
            log(name, f"Error: {e}")
        time.sleep(2 + (time.time() % 1))  # 2-3s delay

if __name__ == "__main__":
    main() 


    