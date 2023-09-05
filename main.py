import pathlib
import pprint
import re, requests, bs4, csv, os
import time
from csv import DictWriter
from pathlib import Path
from celery.app.control import Inspect
from database import Session, Parts
from tqdm import tqdm

from tasks import download_pdf, app

if 'price_of_parts.csv' in os.listdir():
    os.remove('price_of_parts.csv')
url = 'https://lvtrade.ru'


class Lvparser():
    '''Класс парсера
    в init помещены headers и создание папки для хранения картинок, при инициализации экземплера класса
    также размещены пути к папке и основной URL сайта'''
    def __init__(self):
        self.HEADERS = {
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'content-type': 'text/html; charset=UTF-8',
            'Accept-language': 'ru-RU,ru;q=0.9',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'no-store, no-cache, must-revalidate',
            'If-None-Mathe': 'W/"67ab43", "54ed21", "7892dd"',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'content-type': 'text/html; charset=UTF-8'
        }
        if 'Pictures' not in os.listdir():
            os.mkdir('Pictures')
        if 'details' not in os.listdir():
            os.mkdir('details')
        self.url = 'https://lvtrade.ru'
        self.url_catalogs = '/catalog/zapchasti/'
        self.path = os.path.join(Path.cwd())
        self.path_to_details = self.path + '/details'

    # Функция получает request по-указанному URL, если сервер уходит в тротлинг, то через паузу вызывает себя снова
    def getinfo(self, url):
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code != 200:
            print('Ошибка получения данных, повторяю попытку (status_code != 200)')
            time.sleep(2)
            self.getinfo(url)
        else:
            data = response.text
        return data

    def getPrices(self):  # Основная функция, вызывающая все остальные
        count = 0
        mother_link = 'https://lvtrade.ru/catalog/zapchasti/'
        text = self.getinfo(mother_link)
        soup = bs4.BeautifulSoup(text, features='html.parser')
        quantity_pages = soup.find_all(class_='nums')[0].text.split(sep="\n")[-2]
        with tqdm(range(0, int(quantity_pages)+1)) as pbar:
        # for num in range(0, int(quantity_pages)+1):
            for num in pbar:
                pbar.set_description(desc=str(num), refresh=True)
                link = f'https://lvtrade.ru/catalog/zapchasti/?PAGEN_1={num}'
                souper = bs4.BeautifulSoup(self.getinfo(link), features='html.parser')
                parts = souper.find_all(class_='item_info')
                for part in parts:
                    name = part.contents[1].contents[3].text.strip()[9:]
                    code = part.contents[1].contents[3].text.strip()[0:7]
                    href = self.url+part.contents[1].contents[3].contents[1].attrs['href']
                    self.download_picture(item_link=href, article=code)
                    try:
                        price = float(part.contents[3].contents[1].contents[1].contents[1].attrs['data-value'])
                    except:
                        price = 0.00
                    with Session as session:
                        item = session.query(Parts).filter_by(code=code).first()
                        if item != None:
                            item.price = price
                            session.commit()
                        else:
                            part = Parts(
                                name=name,
                                code=code,
                                price=price
                            )
                            session.add(part)
                            session.commit()

    def writeData(self, new_row):  # функция, которая записывает данные в CSV файл
        with open(f"price_of_parts.csv", 'a', newline='', encoding='UTF-8') as csvfile:
            headers_csv = ['article', 'name', 'price', 'category']
            writer_newrow = DictWriter(csvfile, fieldnames=headers_csv)
            writer_newrow.writerow(new_row)
            csvfile.close()

    def download_picture(self, item_link, article):
        folder = os.path.join(Path.cwd(), 'Pictures')
        ''' Проверка того, что в папке нет фото запчасти '''
        if f'{article}.jpg' not in os.listdir(folder):
            text = self.getinfo(item_link)
            data = bs4.BeautifulSoup(text, features='html.parser')
            img_link_f = data.find_all(class_='product-detail-gallery__container')
            res_link = img_link_f[0].contents[1].attrs['href']
            if res_link == '/local/templates/aspro_max/images/svg/noimage_product.svg':
                pass
            else:
                r = requests.get(f'{self.url}{res_link}')
                with open(os.path.join(folder, f'{article}.jpg'), 'wb') as f:
                    if os.path.join(folder, f'{article}.jpg') not in os.listdir(folder):
                        f.write(r.content)
                    else:
                        pass
        else:
            pass

    def get_detailing(self):
        ''' Метод класса, который позволяет сохранять деталировки в pdf формате
         содержит два списка: список ссылок и список каталогов, каждый из которых соответствует производителю оборудования'''
        list_links = []
        folders_list = []
        tasks_list = []
        list_of_files = []
        for root, dirs, files in os.walk(self.path_to_details):
            list_of_files.extend(files)
        link = f'{self.url}/detailing/'
        text = self.getinfo(url=link)
        soup = bs4.BeautifulSoup(text, features='html.parser')
        elements = soup.find_all(class_='detailing-content__tr')
        for element in elements:
            href = f'{self.url}{element.contents[7].contents[3].attrs["href"]}'
            name = f'{element.contents[5].contents[3].text.replace("/", "_")}.pdf'
            ''' Проверка того, что файл уже не скачан и не находится в каталоге загрузок '''
            if name in list_of_files:
                pass
            else:
                folder_name = str(element.contents[1].contents[3].text)
                list_links.append({
                    name: (href, folder_name)
                })
                if folder_name not in folders_list:
                    folders_list.append(folder_name)
        for folder in folders_list:
            if folder not in os.listdir(self.path_to_details):
                os.mkdir(os.path.join(self.path_to_details, folder))
        if len(list_links) == 0:
            return print('Все файлы уже скачаны')
        else:
            for item in list_links:
                for name, object in item.items():
                    res = download_pdf.delay(name=name, link=object[0], folder_name=object[1], path=self.path_to_details)
                    tasks_list.append(res)
        with tqdm(tasks_list) as pbar:
            pbar.set_description(desc=f'Идет скачивание {len(tasks_list)} деталировок...')
            for task in pbar:
                while task.status == 'PENDING':
                    pass
                else:
                    pbar.update(1)
        return print('Все задачи успешно выполнены')

if __name__ == "__main__":
    Lvparser = Lvparser()
    # Lvparser.getPrices()
    Lvparser.get_detailing()
