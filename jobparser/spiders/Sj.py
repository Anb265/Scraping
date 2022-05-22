import scrapy
from scrapy.http import HtmlResponse, TextResponse
from jobparser.items import JobparserItem

SJ_URL = 'https://www.superjob.ru/vacancy/search/?keywords='


class SjSpider(scrapy.Spider):
    name = 'Sj'
    allowed_domains = ['superjob.ru']
    max_page_number = 4
    start_urls = ['http://superjob.ru/']

    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [SJ_URL + query]

    @staticmethod
    def parse_item(response: TextResponse):
        title_xpath = '//h1//text()'
        salary_xpath = '///span[contains(@class, "_4Gt5t _2nJZK")]//text()'
        title = response.xpath(title_xpath).getall()
        salary = response.xpath(salary_xpath).getall()
        item = JobparserItem()
        item["title"] = title
        item["salary"] = salary
        item["url"] = response.url
        item["site"] = response.meta['download_slot']
        yield item

    def parse(self, response: TextResponse, page_number: int = 1, **kwargs):
        items = response.xpath('//div[contains(@class, "vacancy-item")]//a[contains(@href, "vakansii")]')
        for item in items:
            url = item.xpath("./@href").get()
            yield response.follow(url, callback=self.parse_item)
        print()
        next_url_xpath = '//div//span[text() = "Дальше"]/ancestor::a/@href'
        next_url = response.xpath(next_url_xpath).get()
        if next_url and page_number < self.max_page_number:
            new_kwargs = {
                "page_number": page_number + 1,
            }
            yield response.follow(
                next_url,
                callback=self.parse,
                cb_kwargs=new_kwargs
            )
