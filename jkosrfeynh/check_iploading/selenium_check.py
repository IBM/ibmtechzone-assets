from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os



def initialize_driver():
    # Initialize the WebDriver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    return driver

# Usage
url=os.environ["url"]
driver = initialize_driver()
driver.get(url)
