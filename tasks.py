from celery import Celery
import requests
import os

app = Celery(broker='redis://127.0.0.1/1', backend='redis://127.0.0.1/2')

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