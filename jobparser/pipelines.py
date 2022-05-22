from pprint import pprint
from itemadapter import ItemAdapter
from pymongo import MongoClient

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB = "jobs"


class JobparserPipeline:
    def __init__(self):
        self.client = MongoClient(MONGO_HOST, MONGO_PORT)
        self.db = self.client[MONGO_DB]

    @staticmethod
    def hh_process_salary(salary_list: list):
        if 'от' in salary_list[0]:
            min_salary = int(salary_list[1].replace('\xa0', ''))
            currency = salary_list[-2]
            if 'до' in salary_list[2]:
                max_salary = int(salary_list[3].replace('\xa0', ''))
            else:
                max_salary = None
        elif 'до' in salary_list[0]:
            min_salary = None
            max_salary = int(salary_list[1].replace('\xa0', ''))
            currency = salary_list[-2]
        else:
            min_salary, max_salary, currency = None, None, None

        return min_salary, max_salary, currency

    @staticmethod
    def sj_process_salary(salary_list: list):
        min_salary, max_salary, currency = None, None, 'руб.'
        if salary_list[0] == 'от':
            min_salary = int(salary_list[2].replace('\xa0', '').replace('руб.', ''))

        elif salary_list[0] == 'до':
            max_salary = int(salary_list[2].replace('\xa0', '').replace('руб.', ''))

        elif salary_list[0].replace('\xa0', '').isdigit():
            min_salary = int(salary_list[0].replace('\xa0', ''))
            max_salary = int(salary_list[4].replace('\xa0', ''))
        else:
            min_salary, max_salary, currency = None, None, None

        return min_salary, max_salary, currency

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            salary = self.hh_process_salary(item["salary"])
        else:
            salary = self.sj_process_salary(item["salary"])
        item["salary_min"], item["salary_max"], item["salary_currency"] = salary
        item["title"] = " ".join(item["title"])
        del item['salary']

        collection = self.db[spider.name]
        # collection.delete_many({})
        collection.update_one(item, {"$set": item}, upsert=True)

        return item
