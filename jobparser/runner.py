from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.settings import Settings
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.Sj import SjSpider

configure_logging()
settings = get_project_settings()
runner = CrawlerRunner(settings)

# search_vacancy = 'python'
search_vacancy = str(input('Введите вакансию для поиска: '))
hhru_kwargs = {"query": search_vacancy}
runner.crawl(HhruSpider, **hhru_kwargs)
runner.crawl(SjSpider, **hhru_kwargs)

d = runner.join()
d.addBoth(lambda _: reactor.stop())

reactor.run()

# if __name__ == '__main__':
#     crawler_settings = Settings()
#     crawler_settings.setmodule(settings)
#
#     process = CrawlerProcess(settings=crawler_settings)
#
#     search_vacancy = 'python'  # str(input('Введите вакансию для поиска: '))
#     hhru_kwargs = {"query": search_vacancy}
#
#     process.crawl(HhruSpider, **hhru_kwargs)
#     process.crawl(SjSpider, **hhru_kwargs)
#     process.start()
