from dotenv import load_dotenv
import os
import requests

load_dotenv("./.env")
API_key = os.environ["API_KEY"]
city_name = str(input('Введите название города на английском: '))


def weather_now(city_name):
    url = 'https://api.openweathermap.org/data/2.5/weather?'
    params = {'q': city_name, 'appid': API_key}
    r = requests.get(url, params=params)
    r = r.json()
    return f'В городе {r.get("name")} {round(r.get("main").get("temp") - 273, 2)} градусов'


print(weather_now(city_name))
