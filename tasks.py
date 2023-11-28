import shutil

from celery import Celery
import requests
import os
import bs4
import pathlib
import time
from pathlib import Path
from PyPDF2 import  PdfReader, PdfWriter
from typing import Union, Literal, List

app = Celery(broker='redis://127.0.0.1/1', backend='redis://127.0.0.1/2')

HEADERS = {
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

def getinfo(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(url)
        print('Ошибка получения данных, повторяю попытку (status_code != 200)')
        time.sleep(0.33)
        getinfo(url)
    else:
        data = response.text
    return data

@app.task(rate_limit='30/m')
def download_pdf(name, link, folder_name, path):
    ''' Функция принимает на вход: название файла, ссылку на его скачивание, название папки для сохранения, а также, путь к корневому каталогу '''
    path_to_save = os.path.join(path, folder_name)
    print(path_to_save)
    if f'{name}.pdf' not in os.listdir(path_to_save):
        ''' После проверки на то, что такая деталировка еще не скачана, файл сохраняется в нужный каталог '''
        response = requests.get(url=link)
        with open(os.path.join(path_to_save, name), 'wb') as file:
            file.write(response.content)
    return 'Done'

@app.task(rate_limit='20/m')
def download_picture(item_link, article):
    folder = os.path.join(pathlib.Path.cwd(), 'Pictures')
    ''' Проверка того, что в папке нет фото запчасти '''
    if f'{article}.jpg' not in os.listdir(folder):
        text = getinfo(url=item_link)
        data = bs4.BeautifulSoup(text, features='html.parser')
        img_link_f = data.find_all(class_='product-detail-gallery__container')
        res_link = img_link_f[0].contents[1].attrs['href']
        if res_link == '/local/templates/aspro_max/images/svg/noimage_product.svg':
            return None
        else:
            r = requests.get(f'https://lvtrade.ru{res_link}')
            with open(os.path.join(folder, f'{article}.jpg'), 'wb') as f:
                if os.path.join(folder, f'{article}.jpg') not in os.listdir(folder):
                    f.write(r.content)
                    return 'ok'
                else:
                    return None
    else:
        return None


@app.task()
def stamp(
        content_pdf: Path,
        stamp_pdf: Path,
        pdf_result: Path,
        page_indices: Union[Literal["ALL"], List[int]] = "ALL",
):
    reader = PdfReader(stamp_pdf)
    image_page = reader.pages[0]

    writer = PdfWriter()
    try:
        reader = PdfReader(content_pdf)
    except:
        shutil.copy(content_pdf, 'Не обработано')
    if page_indices == "ALL":
        page_indices = list(range(0, len(reader.pages)))
    for index in page_indices:
        content_page = reader.pages[index]
        mediabox = content_page.mediabox
        content_page.merge_page(image_page)
        content_page.mediabox = mediabox
        try:
            writer.add_page(content_page)
        except:
            pass

    with open(pdf_result, "wb") as fp:
        try:
            writer.write(fp)
        except:
            print('Не скопировано')