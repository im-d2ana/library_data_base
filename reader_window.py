import tkinter as tk
from reader_actions import *

def open_reader_window():
    win = tk.Toplevel()
    win.title("Читатель")
    win.geometry("450x150")
    
    buttons = [
        ("Посмотреть каталог экземпляров", view_catalog),
        ("Найти экземпляр", search_catalog),
        ("Посмотреть историю выдач", issue_history),
        ("Отчет о прочитанных экземплярах", report_read)
    ]

    for text, cmd in buttons:
        tk.Button(win, text=text, width=50, command=cmd).pack(pady=3)