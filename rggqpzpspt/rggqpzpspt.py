from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import unicodedata


def clean_text(text):
    cleaned_text = unicodedata.normalize("NFKD", text)
    return cleaned_text


def get_text_from_url(url):
    try:
        # Set up Chrome options with the provided User-Agent header
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('user-agent=' + 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')

        # Set up a Chrome WebDriver with the specified options
        driver = webdriver.Chrome(options=chrome_options)

        # Open the URL
        driver.get(url)

        # Wait for the content to load, e.g., wait for a specific element to be present
        #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "your_element_id")))
        driver.implicitly_wait(5000)

        # Get the page source after dynamic content has loaded
        page_source = driver.page_source

        # Close the WebDriver
        driver.quit()

        # Use BeautifulSoup to parse the page source
        #parsed_data = BeautifulSoup(page_source, "html.parser")
        parsed_data = BeautifulSoup(page_source, "html.parser")

#
        #print(parsed_data.meta['charset'])
        raw_text = parsed_data.get_text()
        cleaned_text = clean_text(raw_text)
        
    
        return {"url": url, "text": cleaned_text}
    except Exception as e:
        print(f"An error occurred for URL {url}: {e}")
        return {"url": url, "text": None}



if __name__ == "__main__":
    # Specify the path to the file containing URLs
    urls_file_path = "links.txt"

    # Read URLs from the file
    with open(urls_file_path, "r") as file:
        urls = file.read().splitlines()

    # Extract text for each URL
    extracted_data = []
    for url in urls:
        result = get_text_from_url(url)
        extracted_data.append(result)

    #Save data to Json file
    with open("selenium_extracted_data.json", "w") as json_file:
        json.dump(extracted_data, json_file, indent=4, ensure_ascii=False)
