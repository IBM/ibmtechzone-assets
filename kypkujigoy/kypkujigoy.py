from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os

# selenium 3
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())

def initialize_driver():
    # Initialize the WebDriver
    #driver = webdriver.Chrome(ChromeDriverManager().install())
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

    
    return driver

# Usage
url=os.environ("url")
driver = initialize_driver()
driver.get(url)
