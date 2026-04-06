import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import json
import os

PROFILES_FILE = "profiles.json"

def load_profiles():
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_profiles(profiles):
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

def select_files():
    file_paths = filedialog.askopenfilenames(
        title="Выберите Python файлы",
        filetypes=[("Python files", "*.py")]
    )
    if file_paths:
        entry_files.delete("1.0", tk.END)
        for path in file_paths:
            entry_files.insert(tk.END, path + "\n")

def select_icon():
    icon_path = filedialog.askopenfilename(
        title="Выберите иконку",
        filetypes=[("Icon files", "*.ico")]
    )
    if icon_path:
        entry_icon.delete(0, tk.END)
        entry_icon.insert(0, icon_path)

def select_output_dir():
    folder = filedialog.askdirectory(title="Выберите папку для сохранения")
    if folder:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, folder)

def run_build(files, onefile, noconsole, icon, output_dir, mode):
    cmd = ["pyinstaller"]

    # Настройки в зависимости от режима
    if mode == "Release":
        cmd.append("--onefile")
        cmd.append("--noconsole")
    elif mode == "Debug":
        cmd.append("--onefile")

    if icon:
        cmd.append(f"--icon={icon}")
    if output_dir:
        cmd.append(f"--distpath={output_dir}")

    cmd.extend(files)

    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Читаем поток построчно
    for line in iter(process.stdout.readline, ''):
        if not line:
            break
        text_log.insert(tk.END, line)
        text_log.see(tk.END)

    process.stdout.close()
    process.wait()

    if process.returncode == 0:
        messagebox.showinfo("Готово", f"Сборка завершена успешно!\nФайл сохранён в: {output_dir or 'dist'}")
    else:
        messagebox.showerror("Ошибка", "Сборка завершилась с ошибкой.")

def build_exe():
    files = entry_files.get("1.0", tk.END).strip().splitlines()
    if not files:
        messagebox.showerror("Ошибка", "Выберите хотя бы один файл для компиляции!")
        return
    text_log.delete(1.0, tk.END)
    onefile = var_onefile.get()
    noconsole = var_noconsole.get()
    icon = entry_icon.get()
    output_dir = entry_output.get()
    mode = mode_var.get()
    threading.Thread(target=run_build, args=(files, onefile, noconsole, icon, output_dir, mode), daemon=True).start()

def load_profile():
    name = profile_var.get()
    if name in profiles:
        data = profiles[name]
        entry_files.delete("1.0", tk.END)
        for f in data.get("files", []):
            entry_files.insert(tk.END, f + "\n")
        var_onefile.set(data.get("onefile", True))
        var_noconsole.set(data.get("noconsole", False))
        entry_icon.delete(0, tk.END)
        entry_icon.insert(0, data.get("icon", ""))
        entry_output.delete(0, tk.END)
        entry_output.insert(0, data.get("output_dir", ""))
        mode_var.set(data.get("mode", "Release"))

def save_profile():
    name = profile_var.get()
    if not name:
        messagebox.showerror("Ошибка", "Введите имя профиля!")
        return
    profiles[name] = {
        "files": entry_files.get("1.0", tk.END).strip().splitlines(),
        "onefile": var_onefile.get(),
        "noconsole": var_noconsole.get(),
        "icon": entry_icon.get(),
        "output_dir": entry_output.get(),
        "mode": mode_var.get()
    }
    save_profiles(profiles)
    messagebox.showinfo("Сохранено", f"Профиль '{name}' сохранён!")

root = tk.Tk()
root.title("Сборка .exe")

profiles = load_profiles()

tk.Label(root, text="Профиль:").pack(pady=5)
profile_var = tk.StringVar()
profile_entry = tk.Entry(root, textvariable=profile_var, width=30)
profile_entry.pack(pady=5)
tk.Button(root, text="Загрузить профиль", command=load_profile).pack(pady=2)
tk.Button(root, text="Сохранить профиль", command=save_profile).pack(pady=2)

tk.Label(root, text="Файлы для компиляции:").pack(pady=5)
entry_files = tk.Text(root, height=5, width=60)
entry_files.pack(pady=5)
tk.Button(root, text="Выбрать файлы", command=select_files).pack(pady=5)

var_onefile = tk.BooleanVar(value=True)
var_noconsole = tk.BooleanVar(value=False)

tk.Checkbutton(root, text="--onefile (один exe)", variable=var_onefile).pack(anchor="w")
tk.Checkbutton(root, text="--noconsole (без консоли)", variable=var_noconsole).pack(anchor="w")

tk.Label(root, text="Иконка (.ico):").pack(pady=5)
entry_icon = tk.Entry(root, width=50)
entry_icon.pack(pady=5)
tk.Button(root, text="Выбрать иконку", command=select_icon).pack(pady=5)

tk.Label(root, text="Папка для сохранения:").pack(pady=5)
entry_output = tk.Entry(root, width=50)
entry_output.pack(pady=5)
tk.Button(root, text="Выбрать папку", command=select_output_dir).pack(pady=5)

tk.Label(root, text="Режим сборки:").pack(pady=5)
mode_var = tk.StringVar(value="Release")
tk.Radiobutton(root, text="Release (чистый exe)", variable=mode_var, value="Release").pack(anchor="w")
tk.Radiobutton(root, text="Debug (с консолью)", variable=mode_var, value="Debug").pack(anchor="w")

tk.Button(root, text="Собрать .exe", command=build_exe).pack(pady=10)

text_log = tk.Text(root, height=20, width=80)
text_log.pack(pady=10)

root.mainloop()
