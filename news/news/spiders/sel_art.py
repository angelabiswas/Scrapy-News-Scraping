from pathlib import Path

import scrapy, re
import json



class ArticlesSpider(scrapy.Spider):
    name = "livemint"
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
            "https://www.livemint.com/news/india",
            "https://www.livemint.com/news/world",
            "https://www.livemint.com/companies",
            "https://www.livemint.com/money"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"playwright": True })

    def parse(self, response):
        urls = response.css('h2.headline a::attr(href)').getall()
        urls = list(set(urls))
        for url in urls:
            yield scrapy.Request(url=f"https://www.livemint.com{url}", callback=self.article_parse)
        
        

    def article_parse(self, response):
        text = response.css('div.storyParagraph p::text').getall()
        article_txt = self.clean_text(text)
        author_txt = response.css("div.storyPage_authorDesc__zPjwo a strong::text").get()
        if( author_txt  is None):
            author_txt = response.css("div.storyPage_authorDesc__zPjwo::text").get()
        author_url = response.css("div.storyPage_authorDesc__zPjwo a::attr(href)").get()
        article_info = {
            "url": response.url,
            "content": article_txt,
            "title": response.css("title::text").get(),
            "date/time": response.css("div.storyPage_date__JS9qJ span::text").get(),
            "author": author_txt,
            "author_url": author_url
        }
        if(text != []):
            self.articles.append(article_info)
        return
    
    def close(self, reason):
        with open('livemint_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=4)
    

