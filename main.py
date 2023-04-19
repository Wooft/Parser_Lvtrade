import re, requests, bs4, csv, os
import time
from csv import DictWriter
from pathlib import Path

from tqdm import tqdm

if 'price_of_parts.csv' in os.listdir():
    os.remove('price_of_parts.csv')
url = 'https://lvtrade.ru'


class Lvparser():
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


    def getinfo(self, url):
        response = requests.get(url, headers=self.HEADERS)
        if response.status_code != 200:
            print('Ошибка получения данных, повторяю попытку (status_code != 200)')
            time.sleep(2)
            self.getinfo(url)
        else:
            data = response.text
        return data
    def getCategories(self) -> list:  # Эта функция позволяет получить список всех категорий запчастей на сайте
        text = self.getinfo(self.url + self.url_catalogs)
        datasoup = bs4.BeautifulSoup(text, features="html.parser")
        categories = datasoup.find_all(class_='section-compact-list__image flexbox flexbox--row')
        links = []
        for category in categories:
            for item in category.find_all('a'):
                data = (item.contents[0].get('title'), item.get('href'))
                links.append(data)
        self.getNumbers(datasoup)
        return links

    def getNumbers(self, datasoup):  # Эта функция позволяет получить полное количество всех запчастей на сайте
        countes = datasoup.find_all(class_="element-count2 muted font_upper")
        pattern = re.compile("[0-9]+")
        num = 0
        for count in countes:
            result = pattern.findall(count.text)
            num += int(result[0])
        print(f'Количество запчастей на сайте: {num}')
        return count

    def getPrices(self):  # Основная функция, вызывающая все остальные
        list_links = self.getCategories()
        for item in list_links:
            link = url + item[1]
            text = self.getinfo(link)
            soup = bs4.BeautifulSoup(text, features='html.parser')
            pages = self.getPages(soup)
            pagetitle = soup.find_all(id='pagetitle')[0].text
            with tqdm(pages) as pbar:
                pbar.set_description(pagetitle)
                for page in pbar:
                    pbar.set_postfix(link=link+page, refresh=True)
                    pbar.update(0)
                    time.sleep(0.33)
                    text = requests.get(link+page).text
                    soup = bs4.BeautifulSoup(text, features='html.parser')
                    parts = soup.find_all(class_='inner_info')
                    for part in parts:
                        if len(part.contents[3].contents[1].text) <= 2:
                            pass
                        else:
                            price = float(part.contents[3].contents[1].contents[1].contents[1].attrs.get('data-value'))
                            # Получение артикула товара
                            article = part.contents[1].contents[3].contents[1].text.strip()[0:7]
                            # Заполнение словаря данными для записи в CSV файл
                            new_row = {
                                'article': article,
                                'name': part.contents[1].contents[3].contents[1].text.strip()[9:],
                                'price': price,
                                'category': pagetitle,
                            }
                            self.writeData(new_row)
                            # А тут нужно создать таску, которая будет качать картинки
                            if len(part.find_all(class_='section-gallery-wrapper__item _active')) != 0:
                                if part.contents[1].contents[3].attrs.get('href') == None:
                                    pass
                                else:
                                    item_link = part.contents[1].contents[3].attrs['href']
                                    self.download_picture(item_link=item_link, article=new_row['article'])

    def writeData(self, new_row):  # функция, которая записывает данные в CSV файл
        with open(f"price_of_parts.csv", 'a', newline='', encoding='UTF-8') as csvfile:
            headers_csv = ['article', 'name', 'price', 'category']
            writer_newrow = DictWriter(csvfile, fieldnames=headers_csv)
            writer_newrow.writerow(new_row)
            csvfile.close()

    def getPages(self, soup):  # функция, которая позволяет получить количество и список страниц в категории
        numbers = soup.find_all(class_='nums')
        pages_list = []
        if len(numbers) == 0:
            pages_list = ['?PAGEN_1=1']
        else:
            page_cuanty = int(numbers[0].contents[len(numbers[0].contents) - 2].text)
            for i in range(1, page_cuanty + 1):
                pages_list.append(f'?PAGEN_1={i}')
        return pages_list

    def download_picture(self, item_link, article):
        folder = os.path.join(Path.cwd(), 'Pictures')
        if f'{article}.jpg' not in os.listdir(folder):
            text = self.getinfo(self.url + item_link)
            data = bs4.BeautifulSoup(text, features='html.parser')
            img_link_f = data.find_all(id='photo-0')
            res_link = self.url + img_link_f[0].contents[1].contents[1].attrs['data-src']
            r = requests.get(res_link)
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
