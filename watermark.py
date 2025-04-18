import pathlib
import os
from tqdm import tqdm
from pathlib import Path
from typing import Union, List, Literal
import shutil
from PyPDF2 import PdfReader, PdfWriter

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

def add_watermark(input: str, output: str):
    # Нормализация путей для Windows
    input_dir = pathlib.Path(input).resolve()
    output_dir = pathlib.Path(output).resolve()

    # Создаём выходную директорию
    output_dir.mkdir(parents=True, exist_ok=True)

    # Рекурсивный поиск всех PDF-файлов
    pdf_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(pathlib.Path(root) / file)

    # Фильтрация уже обработанных файлов
    processed_files = {f.name for f in output_dir.glob('*.pdf')}
    to_process = [f for f in pdf_files if f.name not in processed_files]

    # Обработка с прогресс-баром
    with tqdm(total=len(to_process), desc='Наложение водяных знаков') as pbar:
        for pdf_path in to_process:
            try:
                # Формируем выходной путь
                out_path = output_dir / pdf_path.name

                # Вызываем функцию напрямую
                stamp(
                    content_pdf=str(pdf_path),
                    stamp_pdf='w-5.pdf',
                    pdf_result=str(out_path)
                )
                pbar.update(1)
                pbar.set_postfix_str(f'Обработан: {pdf_path.name}')
            except Exception as e:
                print(f"\nОшибка при обработке {pdf_path.name}: {str(e)}")
            finally:
                pbar.refresh()
    print(f'\nГотово! Обработано файлов: {len(to_process)}')

if __name__ == '__main__':
    add_watermark('без водяных знаков', 'с водяными знаками')