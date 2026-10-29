import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from db import get_connection

# просмотр каталога
def view_catalog():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            e.инвентарный_номер,
            t.тип,
            k.название,
            CONCAT(a.фамилия, ' ', a.имя, ' ', a.отчество) AS автор,
            j.жанр,
            i.издательство,
            k.год,
            e.статус
        FROM Экземпляр e
        JOIN Книга k ON e.id_книги = k.id_книги
        JOIN Тип t ON k.id_тип = t.id_тип
        JOIN Жанр j ON k.id_жанр = j.id_жанр
        JOIN Издательство i ON e.id_издательство = i.id_издательство
        JOIN Экземпляр_автор ea ON ea.инвентарный_номер = e.инвентарный_номер
        JOIN Автор a ON a.id_автор = ea.id_автора
        WHERE e.deleted = FALSE
        ORDER BY k.название
    """)

    rows = cur.fetchall()
    conn.close()

    win = tk.Toplevel()
    win.title("Каталог экземпляров")
    win.geometry("1100x400")

    columns = (
        "inv", "type", "title", "author",
        "genre", "publisher", "year", "status"
    )

    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    tree.heading("inv", text="Инв. №")
    tree.heading("type", text="Тип")
    tree.heading("title", text="Название")
    tree.heading("author", text="Автор")
    tree.heading("genre", text="Жанр")
    tree.heading("publisher", text="Издательство")
    tree.heading("year", text="Год")
    tree.heading("status", text="Статус")

    for col in columns:
        tree.column(col, width=130, anchor=tk.CENTER)

    for row in rows:
        tree.insert("", tk.END, values=row)

# Поиск экземпляра
def search_catalog():
    def load_data(title=None, author=None, genre=None, publisher=None):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT DISTINCT
                e."инвентарный_номер",
                t.тип,
                k.название,
                CONCAT(a.фамилия, ' ', a.имя, ' ', a.отчество) AS автор,
                j.жанр,
                i.издательство,
                k.год,
                e.статус
            FROM "Экземпляр" e
            JOIN "Книга" k ON e.id_книги = k.id_книги
            JOIN "Тип" t ON k.id_тип = t.id_тип
            JOIN "Жанр" j ON j.id_жанр = k.id_жанр
            JOIN "Издательство" i ON i.id_издательство = e.id_издательство
            JOIN "Экземпляр_автор" ea
                 ON ea."инвентарный_номер" = e."инвентарный_номер"
            JOIN "Автор" a ON a.id_автор = ea.id_автора
            WHERE e.deleted = FALSE
              AND (%s IS NULL OR k.название ILIKE %s)
              AND (%s IS NULL OR a.фамилия ILIKE %s)
              AND (%s IS NULL OR j.жанр = %s)
              AND (%s IS NULL OR i.издательство = %s)
            ORDER BY k.название
        """, (
            title, f"%{title}%" if title else None,
            author, f"%{author}%" if author else None,
            genre, genre,
            publisher, publisher
        ))

        rows = cur.fetchall()
        conn.close()

        for item in tree.get_children():
            tree.delete(item)

        if not rows:
            messagebox.showinfo("Результат поиска", "Экземпляр с такими данными не найден")
        else:
            for row in rows:
                tree.insert("", tk.END, values=row)

    def search():
        load_data(
            title_entry.get().strip() or None,
            author_entry.get().strip() or None,
            genre_combo.get().strip() or None,
            publisher_combo.get().strip() or None
        )

    win = tk.Toplevel()
    win.title("Найти экземпляр")
    win.geometry("1200x550")

    form = tk.Frame(win)
    form.pack(pady=10)

    tk.Label(form, text="Название").grid(row=0, column=0, padx=5, sticky="e")
    title_entry = tk.Entry(form, width=25)
    title_entry.grid(row=0, column=1, padx=5)

    tk.Label(form, text="Автор").grid(row=0, column=2, padx=5, sticky="e")
    author_entry = tk.Entry(form, width=25)
    author_entry.grid(row=0, column=3, padx=5)

    tk.Label(form, text="Жанр").grid(row=1, column=0, padx=5, sticky="e")
    genre_combo = ttk.Combobox(form, width=23, state="readonly")
    genre_combo.grid(row=1, column=1, padx=5)

    tk.Label(form, text="Издательство").grid(row=1, column=2, padx=5, sticky="e")
    publisher_combo = ttk.Combobox(form, width=23, state="readonly")
    publisher_combo.grid(row=1, column=3, padx=5)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT жанр FROM "Жанр" ORDER BY жанр')
    genre_combo["values"] = [row[0] for row in cur.fetchall()]
    cur.execute('SELECT DISTINCT издательство FROM "Издательство" ORDER BY издательство')
    publisher_combo["values"] = [row[0] for row in cur.fetchall()]
    conn.close()

    tk.Button(win, text="Найти", width=20, command=search).pack(pady=10)

    columns = (
        "inv", "type", "title", "author",
        "genre", "publisher", "year", "status"
    )

    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    headers = [
        "Инв. №", "Тип", "Название", "Автор",
        "Жанр", "Издательство", "Год", "Статус"
    ]

    for col, header in zip(columns, headers):
        tree.heading(col, text=header)
        tree.column(col, width=140, anchor=tk.CENTER)
    load_data()

# История выдач
def issue_history():
    def show():
        ticket_number = ticket.get().strip()

        if not ticket_number:
            messagebox.showwarning(
                "Ошибка",
                "Необходимо ввести значение в поле «Читательский билет»"
            )
            return

        if not ticket_number.isdigit() or len(ticket_number) != 4:
            messagebox.showerror(
                "Ошибка",
                "Номер читательского билета должен быть четырёхзначным числом"
            )
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute('SELECT COUNT(*) FROM "Комплект_выдачи" WHERE "номер_читательского_билета" = %s', (ticket_number,))
        if cur.fetchone()[0] == 0:
            messagebox.showinfo("Результат", "Читательский билет не найден или выдач нет")
            conn.close()
            return

        cur.execute("""
            SELECT e."инвентарный_номер",
                   k."название",
                   kv."дата_выдачи",
                   kv."дата_сдачи"
            FROM "Комплект_выдачи" kv
            JOIN "Экземпляр" e ON kv."инвентарный_номер" = e."инвентарный_номер"
            JOIN "Книга" k ON k."id_книги" = e."id_книги"
            WHERE kv."номер_читательского_билета" = %s
            ORDER BY kv."дата_выдачи"
        """, (ticket_number,))

        rows = cur.fetchall()
        conn.close()

        for item in tree.get_children():
            tree.delete(item)

        for row in rows:
            row_display = list(row)
            if row_display[3] is None:
                row_display[3] = "Не сдано"
            tree.insert("", tk.END, values=row_display)

        if not rows:
            messagebox.showinfo("Результат", "История выдач отсутствует")

    win = tk.Toplevel()
    win.title("История выдач")
    win.geometry("600x400")

    tk.Label(win, text="Введите номер читательского билета:").pack(pady=5)
    ticket = tk.Entry(win)
    ticket.pack(pady=5)

    tk.Button(win, text="Показать", command=show).pack(pady=5)

    columns = ("inv_number", "book_title", "issue_date", "return_date")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    headers = ["Инвентарный номер", "Название книги", "Дата выдачи", "Дата сдачи"]
    for col, header in zip(columns, headers):
        tree.heading(col, text=header)
        tree.column(col, width=140, anchor=tk.CENTER)


# Отчет
def report_read():
    def show():
        ticket_number = ticket.get().strip()
        genre_val = genre.get().strip() or None
        author_val = author.get().strip() or None
        publisher_val = publisher.get().strip() or None
        date_from_str = d1.get().strip()
        date_to_str = d2.get().strip()

        if not ticket_number or not date_from_str or not date_to_str:
            messagebox.showwarning(
                "Ошибка",
                "Необходимо заполнить все обязательные поля:\n"
                "Номер читательского билета, дату начала и дату конца периода"
            )
            return

        if not ticket_number.isdigit() or len(ticket_number) != 4:
            messagebox.showerror("Ошибка", "Номер читательского билета должен быть четырёхзначным числом")
            return

        try:
            date_from = datetime.strptime(date_from_str, "%d.%m.%Y")
            date_to = datetime.strptime(date_to_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Даты должны быть в формате дд.мм.гггг")
            return

        if date_from > date_to:
            messagebox.showerror("Ошибка", "Дата начала периода не может быть позже даты конца")
            return

        if date_to > datetime.today():
            messagebox.showerror("Ошибка", "Дата конца периода не может быть позже текущей даты")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute('SELECT COUNT(*) FROM "Комплект_выдачи" WHERE "номер_читательского_билета" = %s', (ticket_number,))
        if cur.fetchone()[0] == 0:
            messagebox.showinfo("Результат", "Читательский билет не найден или выдач нет")
            conn.close()
            return
        
        date_from_str_sql = date_from.strftime("%d.%m.%Y")
        date_to_str_sql = date_to.strftime("%d.%m.%Y")

        query = """
            SELECT DISTINCT k."название",
                            CONCAT(a."фамилия", ' ', a."имя", ' ', a."отчество") AS автор,
                            i."издательство",
                            j."жанр",
                            kv."дата_сдачи"
            FROM "Комплект_выдачи" kv
            JOIN "Экземпляр" e ON kv."инвентарный_номер" = e."инвентарный_номер"
            JOIN "Книга" k ON k."id_книги" = e."id_книги"
            JOIN "Экземпляр_автор" ea ON ea."инвентарный_номер" = e."инвентарный_номер"
            JOIN "Автор" a ON a."id_автор" = ea."id_автора"
            JOIN "Жанр" j ON j."id_жанр" = k."id_жанр"
            JOIN "Издательство" i ON i."id_издательство" = e."id_издательство"
            WHERE kv."номер_читательского_билета" = %s
              AND kv."статус" = 'В наличии'
              AND TO_DATE(kv."дата_сдачи", 'DD.MM.YYYY') BETWEEN TO_DATE(%s, 'DD.MM.YYYY') AND TO_DATE(%s, 'DD.MM.YYYY')
        """

        params = [ticket_number, date_from_str_sql, date_to_str_sql]

        if genre_val:
            query += " AND j.\"жанр\" ILIKE %s"
            params.append(f"%{genre_val}%")
        if author_val:
            query += " AND (a.\"фамилия\" ILIKE %s OR a.\"имя\" ILIKE %s OR a.\"отчество\" ILIKE %s)"
            params.extend([f"%{author_val}%"]*3)
        if publisher_val:
            query += " AND i.\"издательство\" ILIKE %s"
            params.append(f"%{publisher_val}%")

        query += " ORDER BY kv.\"дата_сдачи\""

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        for item in tree.get_children():
            tree.delete(item)

        if not rows:
            messagebox.showinfo("Результат", "По заданным параметрам ничего не найдено")
            return

        for row in rows:
            row_display = list(row)
            if row_display[4] is None:
                row_display[4] = "Не сдано"
            tree.insert("", tk.END, values=row_display)

    win = tk.Toplevel()
    win.title("Отчет о прочитанных экземплярах")
    win.geometry("900x600")

    frame = tk.Frame(win)
    frame.pack(pady=10)

    tk.Label(frame, text="Номер читательского билета*").grid(row=0, column=0, padx=5, sticky="e")
    ticket = tk.Entry(frame)
    ticket.grid(row=0, column=1, padx=5)

    tk.Label(frame, text="Жанр").grid(row=0, column=2, padx=5, sticky="e")
    genre = tk.Entry(frame)
    genre.grid(row=0, column=3, padx=5)

    tk.Label(frame, text="Автор").grid(row=1, column=0, padx=5, sticky="e")
    author = tk.Entry(frame)
    author.grid(row=1, column=1, padx=5)

    tk.Label(frame, text="Издательство").grid(row=1, column=2, padx=5, sticky="e")
    publisher = tk.Entry(frame)
    publisher.grid(row=1, column=3, padx=5)

    tk.Label(frame, text="Дата начала периода* (дд.мм.гггг)").grid(row=2, column=0, padx=5, sticky="e")
    d1 = tk.Entry(frame)
    d1.grid(row=2, column=1, padx=5)

    tk.Label(frame, text="Дата конца периода* (дд.мм.гггг)").grid(row=2, column=2, padx=5, sticky="e")
    d2 = tk.Entry(frame)
    d2.grid(row=2, column=3, padx=5)

    tk.Button(win, text="Сформировать", command=show).pack(pady=10)

    columns = ("title", "author", "publisher", "genre", "return_date")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    headers = ["Название", "Автор", "Издательство", "Жанр", "Дата сдачи"]
    for col, header in zip(columns, headers):
        tree.heading(col, text=header)
        tree.column(col, width=140, anchor=tk.CENTER)