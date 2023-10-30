import pathlib
from pathlib import Path
from typing import Union, Literal, List
import os
from os import PathLike
from PyPDF2 import PdfWriter, PdfReader


def add_watermark():
    out = 'output'
    if out not in os.listdir(pathlib.Path.cwd()):
        os.mkdir('output')
    folders = os.path.join(pathlib.Path.cwd(), 'details')
    for folder in os.listdir(folders):
        if folder not in os.listdir(out):
            os.mkdir(f'{out}/{folder}')
        for file in os.listdir(os.path.join(folders, folder)):
            out_name = f'{os.path.basename(file)}_with_watermark.pdf)'
            print(file)
            if out_name not in os.listdir(os.path.join(out, folder)):
                stamp(content_pdf=os.path.join(folders, f'{folder}/{file}'), stamp_pdf='w-5.pdf', pdf_result=os.path.join(out, f'{folder}/{out_name}'))
            else:
                pass
    return print('Все задачи успешно выполнены')




def stamp(
    content_pdf: Path,
    stamp_pdf: Path,
    pdf_result: Path,
    page_indices: Union[Literal["ALL"], List[int]] = "ALL",
):
    reader = PdfReader(stamp_pdf)
    image_page = reader.pages[0]

    writer = PdfWriter()

    reader = PdfReader(content_pdf)
    if page_indices == "ALL":
        page_indices = list(range(0, len(reader.pages)))
    for index in page_indices:
        content_page = reader.pages[index]
        mediabox = content_page.mediabox
        content_page.merge_page(image_page)
        content_page.mediabox = mediabox
        writer.add_page(content_page)

    with open(pdf_result, "wb") as fp:
        writer.write(fp)

if __name__ == '__main__':
    add_watermark()