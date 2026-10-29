import tkinter as tk
from librarian_actions import *

def open_librarion_window():
    win = tk.Toplevel()
    win.title("Библиотекарь")
    win.geometry("450x350")
    
    buttons = [
        ("Посмотреть экземпляры фонда", view_copies),
        ("Найти экземпляр", search_copy),
        ("Добавить новый экземпляр", add_copy),
        ("Удалить экземпляр", delete_copy),
        ("Оформить читательский билет", add_reader),
        ("Посмотреть список читателей", view_readers),
        ("Добавить комплект выдачи", add_issue),
        ("Редактировать комплект выдачи", edit_issue),
        ("Посмотреть список комплектов выдачи", view_issues)
    ]

    for text, cmd in buttons:
        tk.Button(win, text=text, width=50, command=cmd).pack(pady=3)