from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re

# --- Setup Selenium ---
options = Options()
options.add_argument("--start-maximized")
service = Service()
driver = webdriver.Chrome(service=service, options=options)

# --- Category URLs and Labels ---
categories = {
    "Pain Relief Management": "https://mydawa.com/products/medical-conditions/pain-relief/management",
    "Eye Care": "https://mydawa.com/products/medical-conditions/eye-care",
    "Diabetes": "https://mydawa.com/products/medical-conditions/diabetes",
    "Cough Cold & Flu": "https://mydawa.com/products/medical-conditions/cough-cold-flu",
    "Digestive Health": "https://mydawa.com/products/medical-conditions/stomach-care/-digestive-health",
    "Blood Pressure Monitors": "https://mydawa.com/products/medical-devices/diagnostics/blood-pressure-monitors"
}

all_product_data = []

# --- Loop through each category ---
for category, url in categories.items():
    print(f"\n🔍 Scraping category: {category}")
    driver.get(url)
    time.sleep(10)

    # Close popup if present
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(@class, "klaviyo-close-form") and @aria-label="Close dialog"]')
            )
        ).click()
        print("✅ Popup closed.")
    except:
        print("ℹ️ No popup or already closed.")

    # --- Smart Scroll ---
    print("📜 Scrolling to load all products...")
    last_count = 0
    same_count_rounds = 0
    max_same_count_rounds = 5  # if no new products after X scrolls, stop

    while same_count_rounds < max_same_count_rounds:
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)
        product_tiles = driver.find_elements(By.CSS_SELECTOR, 'div.col-xs-12.prd-top > a')
        current_count = len(product_tiles)
        print(f"Scroll check: Found {current_count} product links")

        if current_count == last_count:
            same_count_rounds += 1
        else:
            same_count_rounds = 0  # reset if new products load

        last_count = current_count

    print(f"✅ Finished scrolling. Total products: {last_count}")

    # --- Collect product links ---
    product_links = [tile.get_attribute('href') for tile in product_tiles if tile.get_attribute('href')]
    print(f"✅ Collected {len(product_links)} product links.")

    # --- Visit each product page ---
    for idx, link in enumerate(product_links, 1):
        try:
            driver.get(link)
            WebDriverWait(driver, 40).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="PageTitle"]/h1'))
            )
            name = driver.find_element(By.XPATH, '//div[@id="PageTitle"]/h1').text.strip()
            try:
                price = driver.find_element(By.XPATH, '//div[@class="prd-price"]/span[@class="price"]').text.strip()
            except:
                price = "Not Available"

            # Extract quantity using regex
            match = re.search(r'\d+\s*(ml|l|mg|g|mcg|kg|tablet[s]?|capsule[s]?|syrup|sachet[s]?|drop[s]?|pieces|tabs|patch|dose[s]?)',
                              name, re.IGNORECASE)
            quantity = match.group(0) if match else ""

            all_product_data.append({
                "Product Name": name,
                "Current Price (KES)": price,
                "Category": category,
                "Quantity": quantity
            })
            print(f"[{idx}/{len(product_links)}] ✅ {name} | {quantity} | {price}")
        except Exception as e:
            print(f"[{idx}] ❌ Failed to scrape {link}: {e}")

# --- Save to CSV ---
df = pd.DataFrame(all_product_data)
df.to_csv("mydawa_products.csv", index=False)
print("\n✅ All data saved to 'mydawa_products.csv'.")

# --- Clean up ---
driver.quit()