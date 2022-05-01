import requests
import json
from pprint import pprint

repo_list = []


def get_user_repositories(username):
    r = requests.get(f'https://api.github.com/users/{username}/repos')
    r = r.json()
    for i in r:
        repo_list.append(i['name'])
    return repo_list


username = str(input("Введите имя пользователя:"))

pprint(get_user_repositories(f'{username}'))
with open('repositories_list.json', 'w') as f:
    json.dump(repo_list, f, indent=2)
