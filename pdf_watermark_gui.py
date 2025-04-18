import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from PyPDF2 import PdfReader, PdfWriter
import shutil
import os
from tqdm import tqdm


class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Watermark Tool")

        # Настройка переменных
        self.input_dir = Path("без водяных знаков")
        self.output_dir = Path("с водяными знаками")
        self.stamp_pdf = Path("w-5.pdf")
        self.progress = 0
        self.running = False

        # Создание элементов интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Фрейм для директорий
        dir_frame = ttk.Frame(self.root, padding="10")
        dir_frame.grid(row=0, column=0, sticky="ew")

        # Входная директория
        ttk.Label(dir_frame, text="Входная директория:").grid(row=0, column=0, sticky="w")
        self.input_entry = ttk.Entry(dir_frame, width=50)
        self.input_entry.grid(row=0, column=1, padx=5)
        self.input_entry.insert(0, str(self.input_dir))
        ttk.Button(dir_frame, text="Обзор...", command=self.select_input).grid(row=0, column=2)

        # Выходная директория
        ttk.Label(dir_frame, text="Выходная директория:").grid(row=1, column=0, sticky="w")
        self.output_entry = ttk.Entry(dir_frame, width=50)
        self.output_entry.grid(row=1, column=1, padx=5)
        self.output_entry.insert(0, str(self.output_dir))
        ttk.Button(dir_frame, text="Обзор...", command=self.select_output).grid(row=1, column=2)

        # Прогресс-бар
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=1, column=0, padx=10, pady=10)

        # Статус
        self.status_label = ttk.Label(self.root, text="Готов к работе")
        self.status_label.grid(row=2, column=0, pady=5)

        # Кнопка запуска
        self.start_button = ttk.Button(self.root, text="Запустить обработку", command=self.toggle_processing)
        self.start_button.grid(row=3, column=0, pady=10)

    def select_input(self):
        path = filedialog.askdirectory(initialdir=self.input_dir)
        if path:
            self.input_dir = Path(path)
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, path)

    def select_output(self):
        path = filedialog.askdirectory(initialdir=self.output_dir)
        if path:
            self.output_dir = Path(path)
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def toggle_processing(self):
        if not self.running:
            self.running = True
            self.start_button.config(text="Остановить")
            thread = threading.Thread(target=self.run_processing)
            thread.start()
        else:
            self.running = False
            self.start_button.config(text="Запустить обработку")

    def update_progress(self, value, max_value):
        self.progress_bar["maximum"] = max_value
        self.progress_bar["value"] = value
        self.status_label.config(text=f"Обработано: {value}/{max_value} файлов")

    def run_processing(self):
        try:
            # Создание директорий если не существуют
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Поиск PDF-файлов
            pdf_files = list(self.input_dir.rglob("*.pdf"))
            to_process = [
                f for f in pdf_files
                if not (self.output_dir / f.name).exists()
            ]

            # Обработка файлов
            for i, pdf_path in enumerate(to_process):
                if not self.running:
                    break

                out_path = self.output_dir / pdf_path.name
                try:
                    self.stamp(
                        content_pdf=pdf_path,
                        stamp_pdf=self.stamp_pdf,
                        pdf_result=out_path
                    )
                except Exception as e:
                    shutil.copy(pdf_path, self.output_dir / "Ошибки")
                    print(f"Error processing {pdf_path}: {e}")

                self.root.after(10, self.update_progress, i + 1, len(to_process))

            messagebox.showinfo("Готово", f"Обработано {len(to_process)} файлов")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

        finally:
            self.running = False
            self.root.after(10, lambda: self.start_button.config(text="Запустить обработку"))

    def stamp(self, content_pdf, stamp_pdf, pdf_result):
        reader = PdfReader(stamp_pdf)
        image_page = reader.pages[0]

        writer = PdfWriter()
        try:
            content_reader = PdfReader(content_pdf)
        except:
            shutil.copy(content_pdf, pdf_result)
            return

        for page in content_reader.pages:
            mediabox = page.mediabox
            page.merge_page(image_page)
            page.mediabox = mediabox
            writer.add_page(page)

        with open(pdf_result, "wb") as fp:
            writer.write(fp)


if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()