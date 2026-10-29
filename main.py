import tkinter as tk
from librarian_window import open_librarion_window
from reader_window import open_reader_window

root = tk.Tk()
root.title("Библиотека")
root.geometry("300x220")

tk.Label(root, text="Информационная система\nБиблиотека",
         font=("Arial", 14)).pack(pady=20)

tk.Button(root, text="Войти как библиотекарь", width=30, command=open_librarion_window).pack(pady=5)
tk.Button(root, text="Войти как читатель", width=30, command=open_reader_window).pack(pady=5)
tk.Button(root, text="Выход", width=30, command=root.quit).pack(pady=5)

root.mainloop()