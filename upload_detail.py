import os
import pathlib
import shutil
import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from pathlib import Path

#Удаление дублирующих слов в названии деталировки
def clean_file_name(file: str):
    regex = r'\b(\w+)(?:\W+\1\b)+'
    return re.sub(regex, r'\1', file, flags=re.IGNORECASE)

#Перевод названия деталировки в верхний регистр, удаление дублирующих слов
def clean_files(source_folder: str):
    root = os.path.join(pathlib.Path.cwd(), source_folder)
    for folder in os.listdir(root):
        files = os.listdir(os.path.join(root, folder))
        for file in files:
            dest_folder = os.path.join(root, folder)
            clean_name = clean_file_name(file=file.upper())
            os.rename(os.path.join(dest_folder, file), os.path.join(dest_folder, clean_name))

#Логин на сайте, возвращает driver с осуществленной авторизацией
def login(url: str):
    driver = webdriver.Chrome()
    driver.get(url)
    login_form = driver.find_element(By.NAME, value='USER_LOGIN')
    password_form = driver.find_element(By.NAME, value='USER_PASSWORD')
    login_form.send_keys('wooftyaa@gmail.com')
    password_form.send_keys('Miwooft_73787')
    submit = driver.find_element(By.NAME, 'Login')
    submit.click()
    return driver

#Основная функция, загружает деталировку на сайт
def get_detail_upload_form(source_folder: str,
                           home_url: str,
                           upload_url: str):
    driver = login(home_url)
    list_dir = os.listdir(os.path.join(pathlib.Path.cwd(), source_folder))
    list_dir.sort()
    for folder in list_dir:
        clean_files(source_folder=source_folder)
        files_path = os.path.join(os.path.join(pathlib.Path.cwd(), source_folder), folder)
        files = os.listdir(files_path)
        files.sort()
        if len(files) == 0:
            print('Отсутсвуют файлы для загрузки')
        else:
            brand_name = folder
            for file in files:
                file_name = ''.join(file.split('.')[0: -1])
                file_path = os.path.join(files_path, file)
                driver.get(upload_url)
                clear_uploads()
                time.sleep(1)
                name = driver.find_element(By.NAME, value='NAME')
                model = driver.find_element(By.NAME, value='PROP[1399][n0]')
                name.send_keys(file_name)
                model.send_keys(file_name)
                download_form = driver.find_element(By.CLASS_NAME, 'adm-fileinput-btn-panel')
                time.sleep(0.3)
                button = download_form.find_element(By.XPATH, "//span[contains(@class, 'adm-btn add-file-popup-btn')]")
                button.click()
                menu = driver.find_element(By.ID, 'bx-admin-prefix')
                send_form = menu.find_element(By.XPATH, "//span[contains(@class,'bx-core-popup-menu-item-text')]")
                send_file = send_form.find_element(By.XPATH, "//input[@type='file']")
                send_file.send_keys(file_path)
                file_size = float(Path(file_path).stat().st_size) * 0.008
                sleep = file_size / 10000
                time.sleep(sleep)
                submit_button = driver.find_element(By.CLASS_NAME, 'adm-btn-save')
                time.sleep(0.5)
                submit_button.click()
                time.sleep(1)
                shutil.move(file_path, 'Details/uploaded') #После успешной выгрузки деталировка перемещается в каталог "uploaded"

#Очистка каталога с выгруженными деталировками
def clear_uploads():
    for file in os.listdir('Details/uploaded'):
        os.remove(os.path.join('Details/uploaded', file))


if __name__ == '__main__':
    source_folder = 'Details/Ready for upload'
    home_url = 'https://bestzip.ru/personal/'
    upload_url = 'https://bestzip.ru/bitrix/admin/iblock_element_edit.php?IBLOCK_ID=86&type=aspro_max_content&lang=ru&find_section_section=451&IBLOCK_SECTION_ID=451&from=iblock_list_admin'
    get_detail_upload_form(source_folder=source_folder,
                           home_url=home_url,
                           upload_url=upload_url)