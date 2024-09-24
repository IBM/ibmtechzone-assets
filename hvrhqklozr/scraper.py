from typing import Any
import scrapy  
import csv
from scrapy.utils.reactor import install_reactor

class Scraper(scrapy.Spider): 
   name = "second" 
   allowed_domains = ["WEBSITE URL NAME GOES HERE WITHOUT WWWW"] 
   start_urls = []

   with open('elval.csv', mode ='r')as file:
        csvFile = csv.reader(file)
        flag = True
        for lines in csvFile:
            if(flag):
                flag = False
                continue
                print(lines[0])
            if(len(lines[0])>5):
                start_urls.append(lines[0])
        print(start_urls)

   def parse(self, response): 
      filename = response.url.split("/")[-2] + '.html' 
      with open(filename, 'wb') as f: 
         f.write(response.body) 


    