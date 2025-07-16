from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import traceback
import os
from datetime import datetime

# Setup WebDriver
def setup_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Click menu functions
def click_tablets_menu(driver, url):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        element = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Tablets")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", element)
        print("✅ Clicked Tablets")
    except:
        print("❌ Couldn't click Tablets")
        traceback.print_exc()

def click_samsung_menu(driver, url):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        element = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Samsung")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        element.click()
        print("✅ Clicked Samsung brand")
    except:
        print("❌ Couldn't click Samsung brand")
        traceback.print_exc()

def click_apple_menu(driver, url):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        element = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Apple")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        element.click()
        print("✅ Clicked Apple brand")
    except:
        print("❌ Couldn't click Apple brand")
        traceback.print_exc()

def click_smartphones_menu(driver, url):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        element = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Smartphones")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        element.click()
        print("✅ Clicked Smartphones")
    except:
        print("❌ Couldn't click Smartphones")
        traceback.print_exc()

# Scroll to bottom of page
def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    time.sleep(2)

# Scrape products on the current page
def scrape_current_page(driver, data):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product")))
        products = driver.find_elements(By.CLASS_NAME, "product")
        print(f"🛒 Found {len(products)} products\n")

        for idx, product in enumerate(products, 1):
            try:
                name = product.find_element(By.CSS_SELECTOR, "h3.heading-title.product-name a").text.strip()
            except:
                name = "N/A"

            try:
                price_element = product.find_element(By.CLASS_NAME, "price")
                ins_prices = price_element.find_elements(By.TAG_NAME, "ins")
                if ins_prices:
                    prices = [el.text.strip() for el in ins_prices]
                    price = " - ".join(prices)
                else:
                    price_spans = price_element.find_elements(By.CLASS_NAME, "woocommerce-Price-amount")
                    prices = [span.text.strip() for span in price_spans]
                    price = " - ".join(prices)
            except:
                price = "N/A"

            print(f"{idx}. {name}\n   Current Price: {price}\n")

            data.append({
                "Product Name": name,
                "Current Price": price
            })

    except Exception:
        print("❌ Error scraping current page")
        traceback.print_exc()

# Go to next page
def click_next_page(driver):
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a.next.page-numbers")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
        time.sleep(1)
        next_button.click()
        print("➡️ Moved to next page...\n")
        return True
    except:
        print("✅ No more pages. Finished.")
        return False

# Run scraping for a given section
def run_scraping_section(driver, click_function, url, filename):
    click_function(driver, url)
    data = []

    while True:
        scroll_to_bottom(driver)
        scrape_current_page(driver, data)
        if not click_next_page(driver):
            break

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"✅ Data saved to {filename}\n")

# Main execution
if __name__ == "__main__":
    url = "https://www.phoneplacekenya.com/"
    driver = setup_driver()

    run_scraping_section(driver, click_tablets_menu, url, "tablets_data.csv")
    run_scraping_section(driver, click_samsung_menu, url, "samsung_data.csv")
    run_scraping_section(driver, click_apple_menu, url, "apple_data.csv")
    run_scraping_section(driver, click_smartphones_menu, url, "smartphones_data.csv")

    driver.quit()

    # Combine all CSVs
    csv_files = ["tablets_data.csv", "samsung_data.csv", "apple_data.csv", "smartphones_data.csv"]
    combined_data = pd.DataFrame()

    for file in csv_files:
        if os.path.exists(file):
            df = pd.read_csv(file)
            df["Category"] = file.replace("_data.csv", "").capitalize()
            combined_data = pd.concat([combined_data, df], ignore_index=True)
        else:
            print(f"⚠️ File not found: {file}")

    # Save combined CSV
    combined_csv_path = r"C:\Users\user\Desktop\Phone Place KE\phone_place_KE.csv"
    combined_data.to_csv(combined_csv_path, index=False, encoding="utf-8-sig")
    print(f"✅ Combined data saved to {combined_csv_path}")

    # Convert CSV to Excel
    current_date = datetime.now().strftime("%d-%m-%Y")
    excel_file = rf"C:\Users\user\Desktop\Phone Place KE\Phone_Place_data_{current_date}.xlsx"

    try:
        df = pd.read_csv(combined_csv_path)
        df.to_excel(excel_file, index=False)
        print(f"✅ Converted to Excel: {excel_file}")

    except FileNotFoundError:
        print(f"❌ File not found: {combined_csv_path}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
