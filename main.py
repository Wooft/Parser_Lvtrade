import re, requests, bs4, csv, os
import time
from csv import DictWriter
from pathlib import Path

from database import Session, Parts
from tqdm import tqdm

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
        self.url = 'https://lvtrade.ru'
        self.url_catalogs = '/catalog/zapchasti/'
        self.path = os.path.join(Path.cwd())

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
                        item = session.query(Parts).filter_by(code=code).all()
                        if len(item) != 0:
                            part = item[0]
                            part.price = price
                            session.add(part)
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

if __name__ == "__main__":
    Lvparser = Lvparser()
    Lvparser.getPrices()
