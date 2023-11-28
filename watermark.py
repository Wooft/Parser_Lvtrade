import pathlib
from pathlib import Path
from typing import Union, Literal, List
import os
from os import PathLike
from PyPDF2 import PdfWriter, PdfReader
from tqdm import tqdm
import shutil
from tasks import stamp


def add_watermark(input: str, output: str):
    folders = os.path.join(pathlib.Path.cwd(), input)
    list_of_files = []
    for root, list, files in os.walk(input):
        list_of_files.extend(files)
    list_tasks = []
    for folder in os.listdir(folders):
        if folder not in os.listdir(output):
            os.mkdir(f'{output}/{folder}')
        for file in os.listdir(os.path.join(folders, folder)):
            ext = file.split('.')[-1]
            if ext != 'pdf':
                pass
            else:
                out_name = f'{os.path.basename(file)}'
                if out_name not in os.listdir(os.path.join(output, folder)):
                    task = stamp.delay(content_pdf=os.path.join(folders, f'{folder}/{file}'), stamp_pdf='w-5.pdf', pdf_result=os.path.join(output, f'{folder}/{out_name}'))
                    list_tasks.append(task)
                    print('добавлено')
                else:
                    pass
    with tqdm(list_tasks) as pbar:
        pbar.set_description(desc=f'Идет обработка {len(list_tasks)} деталировок...')
        for task in pbar:
            while task.status == 'PENDING':
                pass
            else:
                pbar.update(1)
    return print('Все задачи успешно выполнены')