import datetime
import os
import pathlib
import shutil
import time
import csv
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import bs4



def parse(url: str):
    count = 0
    now = datetime.datetime.now()
    driver = webdriver.Chrome()
    driver.get(url)
    login = driver.find_element(by='id', value='UTI_LOGIN_TPL')
    password = driver.find_element(by='id', value='UTI_PASSWORD_TPL')
    login.send_keys('BEST ZIP')
    password.send_keys('BEST ZIP')
    time.sleep(1)
    submit = driver.find_element(by='name', value='submit')
    submit.click()
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, features='html.parser')
    links = soup.find_all(id='par75')
    for link in links[0].contents[1].contents[1].contents:
        if type(link) is not bs4.element.NavigableString:
            driver.get(f'https://www.russia.robot-coupe.eu/{link.contents[1].attrs["href"]}')
            details_page = BeautifulSoup(driver.page_source, features='html.parser')
            table = details_page.find(class_='tpl_modele')
            print()
            for detal in table.contents[1].contents[3].contents:
                if type(detal) is not bs4.element.NavigableString:
                    name = detal.contents[1].text.strip()
                    for url in detal.contents[3].contents:
                        if type(url) is not bs4.element.NavigableString:
                            model = url.text
                            driver.get(f'https://www.russia.robot-coupe.eu/{url.attrs["href"]}')
                            try:
                                pdf_link = driver.find_element(By.CLASS_NAME, "pdf")
                                file_name = \
                                BeautifulSoup(pdf_link.get_attribute('outerHTML'), features='html.parser').contents[
                                    0].attrs['href'].split('=')[-1]
                                pdf_link.click()
                                count += 1
                                time.sleep(5)
                                rename_download_file(download_file=file_name,
                                                     new_name=f'robot coupe {name}_{model}.pdf')
                            except:
                                print(f'https://www.russia.robot-coupe.eu/{url.attrs["href"]} - не смог получить ссылку на скачивание')

                            # try:
                            #     time.sleep(0.5)
                            #     pages_list = driver.find_element(By.ID, 'piecedetachee_lien_0')
                            #     pages = pages_list.find_elements(By.XPATH, '*')
                            # except:
                            #     driver.get(f'https://www.russia.robot-coupe.eu/{url.attrs["href"]}')
                            #     pages_list = driver.find_element(By.ID, 'piecedetachee_lien_0')
                            #     pages = pages_list.find_elements(By.XPATH, '*')
                            # for page in pages:
                            #     page.click()
                            #     info = driver.find_element(By.CLASS_NAME, 'ref')
                            #     same_info = BeautifulSoup(info.get_attribute('outerHTML'))
                            #     data = {
                            #         'ID': same_info.contents[0].contents[1].text,
                            #         'Article': same_info.contents[0].contents[3].text,
                            #         'Name': same_info.contents[0].contents[6].text
                            #     }
                            #     write_to_csv(file_bame=f'{name}_{model}', data=data)
    return print(f'Все задачи выполнены за: {datetime.datetime.now() - now}, скачано {count} файлов')

def write_to_csv(file_bame, data):
    if 'Robocop' not in os.listdir(pathlib.Path.cwd()):
        os.mkdir('Robocop')
    csv_file = os.path.join('Robocop', file_bame)
    if file_bame not in os.listdir('Robocop'):
        with open(csv_file, 'a') as file:
            fieldnames = ['ID', 'Name', 'Article']
            writer = csv.DictWriter(file, fieldnames=fieldnames, dialect='excel')
            writer.writeheader()
            writer.writerow(data)
    else:
        with open(csv_file, 'a') as file:
            fieldnames = ['ID', 'Name', 'Article']
            writer = csv.DictWriter(file, fieldnames=fieldnames, dialect='excel')
            writer.writerow(data)

def rename_download_file(download_file, new_name):
    for file in os.listdir('/home/wooft/Загрузки'):
        new_name.replace('/', '_')
        if file.find(download_file) != -1:
            try:
                os.rename(f'/home/wooft/Загрузки/{file}', f'/home/wooft/Загрузки/{new_name}')
            except:
                print('Не прокатило')
            try:
                shutil.move(f'/home/wooft/Загрузки/{new_name}', 'Robocop')
            except:
                print('Не фортануло')

if __name__ == '__main__':
    # parse()
# print('All notice download')

