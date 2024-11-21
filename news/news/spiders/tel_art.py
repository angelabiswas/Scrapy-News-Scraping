from pathlib import Path

import scrapy, re
import json

class ArticlesSpider(scrapy.Spider):
    name = "Telegraph"
    articles = []


    def clean_text(self, data_list):
        combined_text = ' '.join(data_list)

        cleaned_text = re.sub(r'[\n\t]+', ' ', combined_text)
        cleaned_text = re.sub(r'#[\w\-]+\s*{[^}]+}', '', cleaned_text)
        cleaned_text = re.sub(r'\([^)]*\)', '', cleaned_text)

        cleaned_text = ' '.join(cleaned_text.split())
        
        return cleaned_text
    

    def start_requests(self):
        urls = [
             "https://www.telegraphindia.com/india/page-1",
             "https://www.telegraphindia.com/world/page-1",
             "https://www.telegraphindia.com/business/page-1",
        ]
        for url in urls:
             yield scrapy.Request(url = url, callback= self.parse, meta= {'playwright': True})
             
    def parse(self,response):
        urls = response.css('ul.storylisting li a::attr(href)').getall()
        urls = list(set(urls))
        for url in urls[:5]:
            yield scrapy.Request( url = f"https://www.telegraphindia.com{url}", callback=self.article_parse, meta= {'playwright': True} )
        # print(urls)

    def article_parse(self, response):
        text = response.css('article p::text').getall()
        article_txt = self.clean_text(text)
        author_txt = response.css("div.publishdate strong::text").get()
        
        article_info = {
            "url": response.url,
            "content": article_txt,
            "title": response.css("div.articletsection h1::text").get(),
            "date/time": response.css("div.publishdate ::text").get(),
            "author": author_txt,
            # "author_url": author_url
        }
        print(article_info)
        if(text != []):
            self.articles.append(article_info)
        return
    
    def close(self, reason):
        with open('telegraph_data.json', 'w', encoding= 'utf-8') as f:
            json.dump(self.articles, f, ensure_ascii= False, indent=4)