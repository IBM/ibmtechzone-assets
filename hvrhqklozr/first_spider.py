import scrapy  


"""
class firstSpider(scrapy.spiders.SitemapSpider): 
   name = "first" 
   allowed_domains = ["muellerindustries.com"] 
   
   sitemap_urls = ["https://www.muellerindustries.com/sitemap_sitepages.xml"] 
   
   def parse(self, response):
        print(response.url)
        #return response.url
        yield {'url': response.url}

# --- it runs without project and saves in `output.csv` ---

from scrapy.crawler import CrawlerProcess

c = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0',

    # save in file as CSV, JSON or XML
    'FEED_FORMAT': 'csv',     # csv, json, xml
    'FEED_URI': 'muellerindustries.csv', # 
})
c.crawl(firstSpider)
c.start()"""

"""
   def parse(self, response): 
      filename = response.url.split("/")[-2] + '.html' 
      with open(filename, 'wb') as f: 
         f.write(response.body)"""

