import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from pymongo import errors
from pprint import pprint
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

client = MongoClient('127.0.0.1', 27017)
db = client['vk_posts']
vk_posts = db.vk_posts
# vk_posts.delete_many({})

chrome_options = Options()
chrome_options.add_argument("start-maximized")
driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
driver.implicitly_wait(10)

vk_link = 'https://vk.com/tokyofashion'
search_subject = "Токио"


def search_posts(what_to_find):
    driver.get(vk_link)
    search = driver.find_element(By.XPATH, "//div[contains(@class, 'wall_module')]//a[contains(@class, 'ui_tab_search')]")
    search.click()
    time.sleep(1)
    search = driver.find_element(By.ID, "wall_search")
    search.send_keys(what_to_find)
    time.sleep(0.5)
    search.send_keys(Keys.ENTER)


def scroll_page():
    scroll = 0

    while scroll < 1:
        driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
        try:
            auth_popup = driver.find_element(By.CLASS_NAME, 'UnauthActionBox__close')
            auth_popup.click()
            time.sleep(0.5)
        except:
            pass
        scroll += 1
        time.sleep(1)


def get_vk_posts():
    posts = driver.find_elements(By.XPATH, "//div[contains(@id, 'page_search_posts')]//div[@class='_post_content']")

    for post in posts:
        posts_info = {}
        post_date = post.find_element(By.CLASS_NAME, "post_date").text
        post_text = post.find_element(By.CLASS_NAME, "wall_post_text").text
        time.sleep(3)
        elem = post.find_element(By.CLASS_NAME, "post_link")
        link = elem.get_attribute('href')

        elem = post.find_element(By.CLASS_NAME, "PostBottomAction")
        likes = elem.get_attribute('data-reaction-counts')[1:-1]

        elem = post.find_element(By.XPATH, '//div[contains(@title, "Поделиться")]')
        share = elem.get_attribute('data-count')

        try:
            views = post.find_element(By.CLASS_NAME, '_views').text
        except:
            views = None

        posts_info['post_date'] = post_date
        posts_info['post_text'] = post_text
        posts_info['link'] = link
        posts_info['likes'] = likes
        posts_info['share'] = share
        posts_info['views'] = views

        try:
            vk_posts.update_one(posts_info, {"$set": posts_info}, upsert=True)
        except errors.DuplicateKeyError:
            pass


search_posts(search_subject)
scroll_page()
get_vk_posts()
for doc in vk_posts.find({}):
    pprint(doc)

driver.quit()
