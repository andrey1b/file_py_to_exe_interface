"""
===============================
Программа: Python to EXE Builder
===============================

Как работает программа:
1. Пользователь выбирает файл .py через кнопку «Обзор».
2. При нажатии «Собрать EXE» запускается утилита pyinstaller,
   которая создаёт исполняемый файл (.exe).
3. Весь процесс сборки отображается в окне лога.
4. Лог автоматически сохраняется в папку logs с именем:
   <имя_файла>_log_YYYY-MM-DD_HH-MM.txt
5. Пользователь может:
   - Очистить окно лога («Очистить лог»)
   - Сохранить лог вручную под любым именем («Сохранить лог как...»)
   - Открыть папку logs («Открыть папку логов»)

Используемые модули:
- tkinter: создание графического интерфейса (окна, кнопки, поля ввода).
- filedialog: диалог выбора файлов.
- messagebox: всплывающие окна с сообщениями.
- subprocess: запуск внешних программ (pyinstaller).
- os: работа с файлами и папками.
- datetime: добавление даты и времени в имя файла лога.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
from datetime import datetime

LOGS_DIR = "logs"

def ensure_logs_dir():
    """Создаёт папку logs, если её ещё нет."""
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

def run_build(cmd, text_widget, file_path):
    """Запускает процесс сборки EXE через pyinstaller и сохраняет лог."""
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        log_lines = []

        for line in process.stdout:
            text_widget.insert(tk.END, line)
            text_widget.see(tk.END)
            log_lines.append(line)

        process.wait()

        if process.returncode == 0:
            msg = "\nСборка завершена успешно!\n"
        else:
            msg = f"\nОшибка при сборке, код возврата: {process.returncode}\n"

        text_widget.insert(tk.END, msg)
        log_lines.append(msg)

        ensure_logs_dir()
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        log_file = os.path.join(LOGS_DIR, f"{base_name}_log_{timestamp}.txt")

        with open(log_file, "w", encoding="utf-8") as f:
            f.writelines(log_lines)

    except Exception as e:
        err_msg = f"\nПроизошла ошибка: {e}\n"
        text_widget.insert(tk.END, err_msg)
        ensure_logs_dir()
        log_file = os.path.join(LOGS_DIR, "build_log.txt")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(err_msg)

def select_file():
    """Открывает диалог выбора файла .py и вставляет путь в поле ввода."""
    file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

def build_exe():
    """Запускает сборку выбранного файла в EXE."""
    file_path = entry_file.get()
    if not file_path:
        messagebox.showerror("Ошибка", "Выберите файл .py")
        return

    cmd = ["pyinstaller", "--onefile", file_path]
    text_output.delete(1.0, tk.END)
    run_build(cmd, text_output, file_path)

def clear_log():
    """Очищает окно вывода лога."""
    text_output.delete(1.0, tk.END)

def save_log_as():
    """Сохраняет текущий лог в файл, выбранный пользователем."""
    log_content = text_output.get(1.0, tk.END)
    if not log_content.strip():
        messagebox.showinfo("Информация", "Лог пуст, нечего сохранять.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        title="Сохранить лог как..."
    )
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(log_content)
        messagebox.showinfo("Успех", f"Лог сохранён в файл:\n{file_path}")

def open_logs_folder():
    """Открывает папку logs в проводнике."""
    ensure_logs_dir()
    os.startfile(LOGS_DIR)

# ------------------ Интерфейс ------------------
root = tk.Tk()
root.title("Python to EXE Builder")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

entry_file = tk.Entry(frame, width=40)
entry_file.pack(side=tk.LEFT)

btn_browse = tk.Button(frame, text="Обзор", command=select_file)
btn_browse.pack(side=tk.LEFT, padx=5)

btn_build = tk.Button(root, text="Собрать EXE", command=build_exe)
btn_build.pack(pady=5)

btn_clear = tk.Button(root, text="Очистить лог", command=clear_log)
btn_clear.pack(pady=5)

btn_save_as = tk.Button(root, text="Сохранить лог как...", command=save_log_as)
btn_save_as.pack(pady=5)

btn_open_folder = tk.Button(root, text="Открыть папку логов", command=open_logs_folder)
btn_open_folder.pack(pady=5)

text_output = tk.Text(root, width=80, height=20)
text_output.pack(padx=10, pady=10)

root.mainloop()

# ------------------ Советы новичку ------------------
"""
Советы новичку:
1. Всегда проверяй, что у тебя установлены нужные библиотеки (например, pyinstaller).
2. Если программа не запускается — читай сообщение об ошибке в логе, оно подскажет причину.
3. В tkinter все элементы (кнопки, поля, текстовые окна) нужно сначала создать, а потом "упаковать" (pack).
4. subprocess позволяет запускать внешние программы — это мощный инструмент для автоматизации.
5. os помогает работать с файлами и папками: проверять, создавать, открывать.
6. datetime удобно использовать для отметки времени — например, чтобы логи не перезаписывались.
7. Не бойся экспериментировать: меняй текст кнопок, размеры окон, добавляй новые функции.
8. Комментарии в коде — твои лучшие друзья. Пиши их для себя, чтобы через месяц вспомнить, что делает строка.

Что почитать дальше:
- Основы Python: переменные, типы данных, циклы, условия.
- Работа с файлами: открытие, чтение, запись.
- Модули и пакеты: как подключать и использовать сторонние библиотеки.
- Tkinter: создание окон, работа с layout (pack, grid, place).
- Основы ООП (объектно-ориентированного программирования): классы, методы, наследование.
- Исключения (try/except): как обрабатывать ошибки.
- PyInstaller: дополнительные параметры (иконки, скрытие консоли, добавление ресурсов).
"""
