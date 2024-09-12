from pymongo import MongoClient
from pymongo import errors
import requests
from bs4 import BeautifulSoup
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['vacancies_hh']

db_vacancies = db.db_vacancies
# db_vacancies.delete_many({})


def search_vacancy(vacancy_name, page_number):

    url = 'https://hh.ru/'
    params = {'area': 1,
              'fromSearchLine': True,
              'text': vacancy_name,
              'from': 'suggest_post',
              'customDomain': 1,
              'items_on_page': 20,
              'page': 0}

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}

    for page in range(0, page_number):
        params['page'] = page

        response = requests.get(url+'/search/vacancy', params=params, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        vacancy_list = dom.find_all('div', {'class': 'vacancy-serp-item'})

        for vacancy in vacancy_list:
            name = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).getText()
            link = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).get('href')
            try:
                salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText().replace("\u202f", "")
            except AttributeError:
                salary = None

            if not salary:
                salary_min = None
                salary_max = None
                salary_currency = None

            else:
                salary_list = salary.split()
                if salary_list[0] == "от":
                    salary_min = int(salary_list[1])
                    salary_max = None
                    salary_currency = salary_list[2]
                elif salary_list[0] == "до":
                    salary_min = None
                    salary_max = int(salary_list[1])
                    salary_currency = salary_list[2]
                else:
                    salary_min = int(salary_list[0])
                    salary_max = int(salary_list[2])
                    salary_currency = salary_list[3]

            try:
                db_vacancies.insert_one({'_id': link,               # ссылка уникальна для каждой вакансии
                                         'name': name,
                                         'link': link,
                                         'salary_min': salary_min,
                                         'salary_max': salary_max,
                                         'salary_currency': salary_currency,
                                         'site': url})

            except errors.DuplicateKeyError:
                continue


def required_vacancies(db_collection, salary):
    definite_salary = []
    for vac in db_collection.find({'$or': [{'salary_min': {'$gte': salary}},
                                           {'salary_max': {'$gte': salary}}],
                                   'salary_currency': 'руб.'}):
        definite_salary.append(vac)
    return definite_salary


vacancy_search = 'Python'
page_amount = 5
search_vacancy(vacancy_search, page_amount)

number_of_vacancies = 0
for doc in db_vacancies.find({}):
    number_of_vacancies += 1
    # pprint(doc)

print(f'Количество найденных вакансий: {number_of_vacancies}')

salary_limit = 100000
print(f'Колличество вакансий с заработной платой больше {salary_limit} рублей: '
      f'{len(required_vacancies(db_vacancies, salary_limit))}')
# pprint(required_vacancies(db_vacancies, salary_limit))
