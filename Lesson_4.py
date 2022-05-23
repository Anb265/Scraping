from pymongo import MongoClient
from pymongo import errors
from pprint import pprint
from lxml import html
import requests

client = MongoClient('127.0.0.1', 27017)
db = client['mail_news']
mail_news = db.mail_news
# mail_news.delete_many({})

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36'}
url = 'https://news.mail.ru/'


def get_dom(link):
    response = requests.get(link, headers=headers)
    dom = html.fromstring(response.text)
    return dom


def get_news():
    main_news = get_dom(url).xpath(
        "//div[contains(@data-logger, 'news__MainTopNews')]//ul//li[@class = 'list__item']//a "
        "| //div[contains(@class, 'daynews__item')]//a")
    for news in main_news:
        news_dict = {}
        news_link = news.xpath("./@href")

        add_info = get_dom(news_link[0])
        date = add_info.xpath("//div//span[contains(@class, 'breadcrumbs__item')]//span//@datetime")
        source = add_info.xpath("//div//span[contains(@class, 'breadcrumbs__item')]//a//text()")
        name = add_info.xpath("//div[contains(@class, 'article')]//div[contains(@class, 'hdr')]//h1/text()")

        news_dict['name'] = name[0]
        news_dict['link'] = news_link[0]
        news_dict['date'] = date[0]
        news_dict['source'] = source[0]

        try:
            mail_news.update_one(news_dict, {"$set": news_dict}, upsert=True)
        except errors.DuplicateKeyError:
            pass


for doc in mail_news.find({}):
    pprint(doc)
