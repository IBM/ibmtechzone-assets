# Author: Pinkal Patel

'''
Title : Crawl Website Pages Excluding Hidden Elements with Selenium Library 

Description:
Problem Statment: Problem Statement: While crawling a website page using Watson Discovery, all text is scraped, including hidden elements. This results in duplication and incorrect information being collected.
Solution: Crawl Page excluding hidden elements using Selenium Library.
Input: Webpage link
Output: credit_card_new.txt file having crawl data
'''

import re
from selenium import webdriver
from bs4 import BeautifulSoup as soup
browser = webdriver.Chrome()

input_website_link = "https://www.icicibank.com/personal-banking/cards/credit-card?ITM=nli_cms_cards_credit_cards_header_nav"

def get_text_excluding_hide_tags(html):
    # Parse the HTML content using BeautifulSoup
    #soup = BeautifulSoup(html, 'html.parser')

    # Define a regular expression pattern to match class names containing "hide"
    hide_class_pattern = re.compile(r'\bhide\b')

    # Find all tags with class names matching the pattern and extract their text
    hide_tags = html.find_all(class_=hide_class_pattern)
    
    # Remove the found tags from the soup
    for tag in hide_tags:
        tag.decompose()

    # Get the remaining text from the modified soup
    text_without_hide_tags = html.get_text(separator='\n', strip=True)

    return text_without_hide_tags

browser.get(input_website_link)
source_data = browser.page_source
page_soup = soup(source_data, "html.parser")
links=page_soup.findAll('div',{"class":"filter-content"})
data = []
for each in links:
    #each.unwrap()
    #data.append(each.text)
    data.append(get_text_excluding_hide_tags(each))

print("web page scrap")
with open('credit_card_new.txt','w') as file:
    file.write(data[0])