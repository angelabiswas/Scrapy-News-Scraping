from pathlib import Path

import scrapy, re
import json



class ArticlesSpider(scrapy.Spider):
    name = "articles"
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
            "https://economictimes.indiatimes.com/news/politics",
            "https://economictimes.indiatimes.com/news/india",
            "https://economictimes.indiatimes.com/news/international/us",
            "https://economictimes.indiatimes.com/news/economy/articlelist/1286551815.cms",
            "https://economictimes.indiatimes.com/news/company/corporate-trends"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        urls = response.css('div.botplData a::attr(href)').getall()
        urls = urls + response.css('div.eachStory a::attr(href)').getall()
        urls = list(set(urls))
        # for url in urls:
        for url in urls:
            yield scrapy.Request(url=f"https://economictimes.indiatimes.com{url}", callback=self.article_parse)
        
        

    def article_parse(self, response):
        text = response.css('div.artText ::text').getall()
        article_txt = self.clean_text(text)
        article_info = {
            "url": response.url,
            "content": article_txt,
            "title": response.css("title::text").get(),
            "date/time": response.css("time::text").get(),
            "author": response.css("span.ag::text").get()
        }
        self.articles.append(article_info)
        return
    
    def close(self, reason):
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=4)
    

