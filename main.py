from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import ast

from dotenv import load_dotenv
import os
load_dotenv()

driver = webdriver.Chrome(service=Service(ChromeDriverManager(version='106.0.5249.61').install()))


def login():
    driver.get('https://www.test.de/meintest/login/?target=%2FHandys-und-Smartphones-im-Test-4222793-tabelle%2F')

    username = os.environ.get('PROJECT_USERNAME')
    password = os.environ.get('PROJECT_PASSWORD')

    time.sleep(1)
    username_field = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.NAME, 'username'))
    )
    username_field.send_keys(username)

    password_field = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.NAME, 'password'))
    )
    password_field.send_keys(password)

    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'form'))
    ).submit()


def get_data(page_number: int):
    driver.get(f'https://www.test.de/Handys-und-Smartphones-im-Test-4222793-tabelle/{page_number}/')

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('h1', class_='p-title')
    if title:
        phones = []
        phone_wrappers = soup.find_all('li', class_='product-list-item product-list-item--access')

        for phone_wrapper in phone_wrappers:
            phone = {}

            phone['brand'] = phone_wrapper.find('a', class_ = 'product-list-item__company-link').text
            phone['name'] = phone_wrapper.find('a', class_='product-list-item__name-link').text
            _price = phone_wrapper.find('span', class_='is-price').text
            phone['price'] = ast.literal_eval(_price.replace(',', '.'))

            table_rows = phone_wrapper.find_all('tr')
            row_labels = ['quality', 'basic_functionality', 'camera', 'display', 'battery', 'handling', 'stability']
            for i, label in enumerate(row_labels):
                unformatted = table_rows[i].find_all('td')[1].find_all('span')[1].text
                try:
                    phone[label] = ast.literal_eval('.'.join(re.findall('\d', unformatted)))
                except:
                    print(phone, unformatted)
            phones.append(phone)

        if len(phones) > 0:
            with open(f'phones-{str(page_number)}.json', 'w') as f:
                f.write(str(phones))
    else:
        pass


if __name__ == '__main__':
    total_pages = 17
    login()
    for i in range(total_pages):
        time.sleep(1)
        get_data(i + 1)