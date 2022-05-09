import json

import requests
from bs4 import BeautifulSoup
from pprint import pprint

url = 'https://hh.ru/'
params = {'area': 1,
          'fromSearchLine': True,
          'text': 'Python',
          'from': 'suggest_post',
          'customDomain': 1,
          'page': 0}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}

while True:
    try:
        vacancy_input = str(input('Введите название вакансии: '))
        params['text'] = vacancy_input
        response = requests.get(url+'/search/vacancy', params=params, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        vacancy_list = dom.find_all('div', {'class': 'vacancy-serp-item'})
        last_page_place = dom.find('a', {'data-qa': 'pager-next'}).previous_sibling.find('a', {'data-qa': 'pager-page'})
        last_page = int(last_page_place.find('span').getText())
    except AttributeError:
        print('По данному запросу ничего не найдено. Попробуйте снова')
    else:
        break

vacancies = []
page_number = int(input(f'Введите количество страниц поиска от 1 до {last_page}: '))

for page in range(0, page_number):
    params['page'] = page

    response = requests.get(url+'/search/vacancy', params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancy_list = dom.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancy_list:
        vacancy_data = {}

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
                salary_min = salary_list[1]
                salary_max = None
                salary_currency = salary_list[2]
            elif salary_list[0] == "до":
                salary_min = None
                salary_max = salary_list[1]
                salary_currency = salary_list[2]
            else:
                salary_min = salary_list[0]
                salary_max = salary_list[2]
                salary_currency = salary_list[3]

        vacancy_data['name'] = name
        vacancy_data['link'] = link
        vacancy_data['salary_min'] = salary_min
        vacancy_data['salary_max'] = salary_max
        vacancy_data['salary_currency'] = salary_currency
        vacancy_data['site'] = url

        vacancies.append(vacancy_data)

pprint(vacancies)

with open('vacancies_hh.json', 'w', encoding='utf-8') as f:
    json.dump(vacancies, f, indent=4, ensure_ascii=False)
