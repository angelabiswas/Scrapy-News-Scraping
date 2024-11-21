from pathlib import Path

import scrapy, re
import json

class ArticlesSpider(scrapy.Spider):
    name = "Digital Terminal"
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
             "https://digitalterminal.in/trending",
             "https://digitalterminal.in/smart-phone",
             "https://digitalterminal.in/solutions",
        ]
        for url in urls:
             yield scrapy.Request(url = url, callback= self.parse, meta={"playwright": True })
             
    def parse(self,response):
        urls = response.css('a[aria-label="headline"] ::attr(href)').getall()
        urls = list(set(urls))
        for url in urls[:5]:
          yield scrapy.Request( url = url, callback=self.article_parse, meta={"playwright": True })
        # print(urls)

    def article_parse(self, response):
        text = response.css('div[data-test-id="text"] p::text').getall()
        article_txt = self.clean_text(text)
        author_txt = response.css('a[aria-label= "author-name"]::text').get()
        author_url = response.css('a[aria-label= "author-name"]::attr(href)').get()
        author_url = f'https://digitalterminal.in{author_url}'

        article_info = {
            "url": response.url,
            "content": article_txt,
            "title": response.css("bdi::text").get(),
            "date/time": response.css("time ::text").get(),
            "author": author_txt,
            "author_url": author_url
        }
        print(article_info)
        if(text != []):
            self.articles.append(article_info)
        return
    
    def close(self, reason):
        with open('digital_terminal_data.json', 'w', encoding= 'utf-8') as f:
            json.dump(self.articles, f, ensure_ascii= False, indent=4)