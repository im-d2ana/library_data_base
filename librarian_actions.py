import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta
import re
from db import get_connection

# просмотр экземпляров фонда
def view_copies():
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

# поиск экземпляров
def search_copy():
    def search():
        inv_number = inv_entry.get().strip()

        if not inv_number:
            messagebox.showwarning("Ошибка", "Введите инвентарный номер")
            return

        if not inv_number.isdigit() or len(inv_number) != 4:
            messagebox.showerror(
                "Ошибка",
                "Инвентарный номер должен быть четырехзначным числом"
            )
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
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
            WHERE e."инвентарный_номер" = %s
              AND e.deleted = FALSE
        """, (inv_number,))

        row = cur.fetchone()
        conn.close()

        for item in tree.get_children():
            tree.delete(item)

        if row:
            tree.insert("", tk.END, values=row)
        else:
            messagebox.showinfo("Результат", "Экземпляр не найден")

    win = tk.Toplevel()
    win.title("Поиск экземпляра")
    win.geometry("1200x400")

    form = tk.Frame(win)
    form.pack(pady=10)

    tk.Label(form, text="Инвентарный номер").grid(row=0, column=0, padx=5)
    inv_entry = tk.Entry(form, width=30)
    inv_entry.grid(row=0, column=1, padx=5)

    tk.Button(form, text="Найти", width=15, command=search)\
        .grid(row=0, column=2, padx=10)

    columns = (
        "inv", "type", "title", "author",
        "genre", "publisher", "year", "status"
    )

    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    headers = [
        "Инв. №", "Тип", "Название", "Автор",
        "Жанр", "Издательство", "Год", "Статус"
    ]

    for col, header in zip(columns, headers):
        tree.heading(col, text=header)
        tree.column(col, width=140, anchor=tk.CENTER)

# добавить экземпляр
def add_copy():
    win = tk.Toplevel()
    win.title("Добавление экземпляра")
    win.geometry("650x450")

    form = tk.Frame(win)
    form.pack(pady=10)

    tk.Label(form, text="Инвентарный номер").grid(row=0, column=0, sticky="e", padx=10, pady=5)
    inv_entry = tk.Entry(form, width=30)
    inv_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(form, text="Название").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    title_entry = tk.Entry(form, width=30)
    title_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(form, text="Автор (ФИО)").grid(row=2, column=0, sticky="e", padx=10, pady=5)
    author_entry = tk.Entry(form, width=30)
    author_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(form, text="Год издания").grid(row=3, column=0, sticky="e", padx=10, pady=5)
    year_entry = tk.Entry(form, width=30)
    year_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(form, text="Тип").grid(row=4, column=0, sticky="e", padx=10, pady=5)
    type_combo = ttk.Combobox(form, width=28, state="readonly")
    type_combo.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(form, text="Жанр").grid(row=5, column=0, sticky="e", padx=10, pady=5)
    genre_combo = ttk.Combobox(form, width=28, state="readonly")
    genre_combo.grid(row=5, column=1, padx=10, pady=5)

    tk.Label(form, text="Издательство").grid(row=6, column=0, sticky="e", padx=10, pady=5)
    publisher_combo = ttk.Combobox(form, width=28, state="readonly")
    publisher_combo.grid(row=6, column=1, padx=10, pady=5)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT тип FROM "Тип" ORDER BY тип')
    type_combo["values"] = [row[0] for row in cur.fetchall()]
    cur.execute('SELECT DISTINCT жанр FROM "Жанр" ORDER BY жанр')
    genre_combo["values"] = [row[0] for row in cur.fetchall()]
    cur.execute('SELECT DISTINCT издательство FROM "Издательство" ORDER BY издательство')
    publisher_combo["values"] = [row[0] for row in cur.fetchall()]
    conn.close()

    def save():
        inv_val = inv_entry.get().strip()
        title_val = title_entry.get().strip()
        author_val = author_entry.get().strip()
        year_val = year_entry.get().strip()
        type_val = type_combo.get().strip()
        genre_val = genre_combo.get().strip()
        publisher_val = publisher_combo.get().strip()
        status_val = "В наличии"

        if not all([inv_val, title_val, author_val, year_val, type_val, genre_val, publisher_val]):
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения")
            return

        if not inv_val.isdigit() or len(inv_val) != 4:
            messagebox.showerror("Ошибка", "Инвентарный номер должен состоять из 4 цифр")
            return

        if len(title_val) > 100:
            messagebox.showerror("Ошибка", "Название не должно превышать 100 символов")
            return

        year_int = int(year_val)
        current_year = datetime.now().year
        if year_int > current_year:
            messagebox.showerror("Ошибка", f"Год издания не может быть больше {current_year}")
            return

        fio_parts = author_val.split()
        if len(fio_parts) < 2:
            messagebox.showerror("Ошибка", "ФИО должно содержать минимум имя и фамилию")
            return
        last_name = fio_parts[0]
        first_name = fio_parts[1]
        patronymic = fio_parts[2] if len(fio_parts) >= 3 else ""

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute('SELECT deleted FROM "Экземпляр" WHERE "инвентарный_номер"=%s', (inv_val,))
            row = cur.fetchone()
            if row:
                if row[0] == False:
                    messagebox.showerror("Ошибка", "Экземпляр с таким инвентарным номером уже существует")
                    conn.close()
                    return
                else:
                    messagebox.showwarning("Внимание", "Экземпляр с таким инвентарным номером был удалён.")
                    conn.close()
                    return

            cur.execute("""
                SELECT id_книги FROM "Книга"
                WHERE LOWER(название)=LOWER(%s) AND id_тип=(SELECT id_тип FROM "Тип" WHERE тип=%s)
                  AND id_жанр=(SELECT id_жанр FROM "Жанр" WHERE жанр=%s) AND год=%s
            """, (title_val, type_val, genre_val, year_int))
            row = cur.fetchone()
            if row:
                book_id = row[0]
            else:
                cur.execute("""
                    INSERT INTO "Книга"(id_тип, название, id_жанр, год)
                    VALUES ((SELECT id_тип FROM "Тип" WHERE тип=%s), %s,
                            (SELECT id_жанр FROM "Жанр" WHERE жанр=%s), %s)
                    RETURNING id_книги
                """, (type_val, title_val, genre_val, year_int))
                book_id = cur.fetchone()[0]

            cur.execute("""
                SELECT id_автор FROM "Автор"
                WHERE LOWER(фамилия)=LOWER(%s)
                AND LOWER(имя)=LOWER(%s)
                AND LOWER(отчество)=LOWER(%s)
            """, (last_name, first_name, patronymic))
            row = cur.fetchone()
            if row:
                author_id = row[0]
            else:
                cur.execute("""
                    INSERT INTO "Автор"(фамилия, имя, отчество)
                    VALUES (%s, %s, %s) RETURNING id_автор
                """, (last_name, first_name, patronymic))
                author_id = cur.fetchone()[0]

            cur.execute('SELECT id_издательство FROM "Издательство" WHERE LOWER(издательство)=LOWER(%s)', (publisher_val,))
            row = cur.fetchone()
            publisher_id = row[0]

            cur.execute("""
                INSERT INTO "Экземпляр"("инвентарный_номер", id_книги, id_издательство, статус)
                VALUES (%s, %s, %s, %s)
            """, (inv_val, book_id, publisher_id, status_val))

            cur.execute("""
                INSERT INTO "Экземпляр_автор"("инвентарный_номер", id_автора)
                VALUES (%s, %s)
            """, (inv_val, author_id))

            conn.commit()

            display_fields = ["Инвентарный номер", "Тип", "Название", "Автор", "Жанр", "Издательство", "Год", "Статус"]
            display_values = [inv_val, type_val, title_val, author_val, genre_val, publisher_val, year_val, status_val]

            disp_win = tk.Toplevel()
            disp_win.title("Добавленный экземпляр")
            disp_win.geometry("700x250")

            tree = ttk.Treeview(disp_win, columns=("Field", "Value"), show="headings", height=len(display_fields))
            tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            tree.heading("Field", text="Поле")
            tree.heading("Value", text="Значение")
            tree.column("Field", width=200, anchor=tk.CENTER)
            tree.column("Value", width=480, anchor=tk.CENTER)

            for f, v in zip(display_fields, display_values):
                tree.insert("", tk.END, values=(f, v))

        except Exception as e:
            conn.rollback()
            conn.close()
            messagebox.showerror("Ошибка БД", str(e))

    tk.Button(win, text="Сохранить", width=20, command=save).pack(pady=10)

# удалить экземпляр
def delete_copy():
    def delete():
        inv_val = inv.get().strip()

        if not inv_val:
            messagebox.showerror("Ошибка", "Введите инвентарный номер")
            return

        if not inv_val.isdigit() or len(inv_val) != 4:
            messagebox.showerror("Ошибка", "Инвентарный номер должен состоять из 4 цифр")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT статус, deleted FROM "Экземпляр"
            WHERE "инвентарный_номер" = %s
        """, (inv_val,))
        row = cur.fetchone()

        if not row:
            messagebox.showerror("Ошибка", f"Экземпляр {inv_val} не найден")
            conn.close()
            return

        status, deleted = row
        if deleted:
            messagebox.showerror("Ошибка", f"Экземпляр {inv_val} уже удалён")
            conn.close()
            return

        if status != "В наличии":
            messagebox.showerror("Ошибка", f"Экземпляр {inv_val} нельзя удалить, так как он {status}")
            conn.close()
            return

        try:
            cur.execute("""
                UPDATE "Экземпляр"
                SET deleted = TRUE
                WHERE "инвентарный_номер" = %s
            """, (inv_val,))
            conn.commit()
            messagebox.showinfo("Успех", f"Экземпляр успешно удалён")
            win.destroy()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            conn.close()

    win = tk.Toplevel()
    win.title("Удаление экземпляр")
    win.geometry("300x150")

    tk.Label(win, text="Инвентарный номер").pack(padx=10, pady=5)
    inv = tk.Entry(win)
    inv.pack(padx=10, pady=5)
    tk.Button(win, text="Удалить", width=20, command=delete).pack(pady=10)

# оформить чит билет
def add_reader():
    def save():
        ticket_val = ticket_entry.get().strip()
        fio_val = fio_entry.get().strip()
        age_val = age_entry.get().strip()
        street_val = street_entry.get().strip()
        house_val = house_entry.get().strip()

        if not all([ticket_val, fio_val, age_val, street_val, house_val]):
            messagebox.showerror(
                "Ошибка",
                "Все поля обязательны для заполнения"
            )
            return

        if not ticket_val.isdigit() or len(ticket_val) != 4:
            messagebox.showerror(
                "Ошибка",
                "Номер читательского билета должен состоять из 4 цифр"
            )
            return

        if not fio_val or len(fio_val) > 50:
            messagebox.showerror(
                "Ошибка",
                "ФИО должно быть строкой длиной до 50 символов"
            )
            return

        if not age_val.isdigit() or not (7 <= int(age_val) <= 100):
            messagebox.showerror(
                "Ошибка",
                "Возраст должен быть числом от 7 до 100"
            )
            return

        if not street_val or len(street_val) > 50:
            messagebox.showerror(
                "Ошибка",
                "Название улицы должно быть строкой до 50 символов"
            )
            return

        if not house_val or len(house_val) > 50 or not re.search(r"\d", house_val):
            messagebox.showerror(
                "Ошибка",
                "Поле «Дом» должно содержать цифры"
            )
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1
            FROM Читательский_билет
            WHERE номер_читательского_билета = %s
        """, (ticket_val,))

        if cur.fetchone():
            conn.close()
            messagebox.showerror(
                "Ошибка",
                "Читательский билет с таким номером уже существует"
            )
            return

        cur.execute("""
            INSERT INTO Читательский_билет
            (номер_читательского_билета, фио, возраст, улица, дом)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING
                "номер_читательского_билета",
                фио,
                возраст,
                улица,
                дом
        """, (
            ticket_val,
            fio_val,
            int(age_val),
            street_val,
            house_val
        ))

        row = cur.fetchone()
        conn.commit()
        conn.close()

        for item in tree.get_children():
            tree.delete(item)

        tree.insert("", tk.END, values=row)
        messagebox.showinfo("Успех", "Читательский билет успешно добавлен")

    win = tk.Toplevel()
    win.title("Оформление читательского билета")
    win.geometry("700x450")

    form = tk.Frame(win)
    form.pack(pady=10)

    labels = [
        "№ читательского билета",
        "ФИО",
        "Возраст",
        "Улица",
        "Дом"
    ]

    ticket_entry = tk.Entry(form, width=30)
    fio_entry = tk.Entry(form, width=30)
    age_entry = tk.Entry(form, width=30)
    street_entry = tk.Entry(form, width=30)
    house_entry = tk.Entry(form, width=30)

    entries = [
        ticket_entry,
        fio_entry,
        age_entry,
        street_entry,
        house_entry
    ]

    for i, (label, entry) in enumerate(zip(labels, entries)):
        tk.Label(form, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
        entry.grid(row=i, column=1, padx=10, pady=5)

    tk.Button(
        win,
        text="Сохранить",
        width=20,
        command=save
    ).pack(pady=10)

    columns = ("ticket", "fio", "age", "street", "house")

    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    headers = [
        "№ билета",
        "ФИО",
        "Возраст",
        "Улица",
        "Дом"
    ]

    for col, header in zip(columns, headers):
        tree.heading(col, text=header)
        tree.column(col, width=160, anchor=tk.CENTER)

# список читателей
def view_readers():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            номер_читательского_билета,
            фио,
            возраст,
            улица,
            дом
        FROM Читательский_билет
        ORDER BY фио
    """)

    rows = cur.fetchall()
    conn.close()

    win = tk.Toplevel()
    win.title("Список читателей")
    win.geometry("900x400")

    columns = ("ticket", "fio", "age", "street", "house")

    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    headers = [
        "№ читательского билета",
        "ФИО",
        "Возраст",
        "Улица",
        "Дом"
    ]

    for col, header in zip(columns, headers):
        tree.heading(col, text=header)
        tree.column(col, width=180, anchor=tk.CENTER)

    for row in rows:
        tree.insert("", tk.END, values=row)

# добавить комплект выдачи
def add_issue():
    def save():
        ticket_val = ticket.get().strip()
        inv_val = inv.get().strip()
        issue_date_str = issue_date.get().strip()

        if not all([ticket_val, inv_val, issue_date_str]):
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения")
            return

        if not ticket_val.isdigit() or len(ticket_val) != 4:
            messagebox.showerror("Ошибка", "Номер читательского билета должен состоять из 4 цифр")
            return

        if not inv_val.isdigit() or len(inv_val) != 4:
            messagebox.showerror("Ошибка", "Инвентарный номер должен состоять из 4 цифр")
            return

        try:
            issue_dt = datetime.strptime(issue_date_str, "%d.%m.%Y")
            if issue_dt > datetime.today():
                messagebox.showerror("Ошибка", "Дата выдачи не может быть позже текущей даты")
                return

            return_dt = issue_dt + timedelta(days=14)
            return_date_str = return_dt.strftime("%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата выдачи должна быть в формате дд.мм.гггг")
            return

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT 1 FROM "Читательский_билет"
                WHERE "номер_читательского_билета" = %s
            """, (ticket_val,))
            if not cur.fetchone():
                messagebox.showerror("Ошибка", "Читательский билет не найден")
                return

            cur.execute("""
                SELECT статус, deleted FROM "Экземпляр"
                WHERE "инвентарный_номер" = %s
            """, (inv_val,))
            row = cur.fetchone()

            if not row:
                messagebox.showerror("Ошибка", "Экземпляр не найден")
                return

            status, deleted = row
            if deleted:
                messagebox.showerror("Ошибка", "Экземпляр удалён")
                return

            if status != "В наличии":
                messagebox.showerror("Ошибка", f"Экземпляр сейчас: {status}")
                return

            cur.execute("""
                INSERT INTO "Комплект_выдачи"
                ("номер_читательского_билета", "инвентарный_номер",
                 статус, "дата_выдачи", "дата_сдачи")
                VALUES (%s, %s, 'Выдан', %s, %s)
                RETURNING id_выдачи
            """, (
                ticket_val,
                inv_val,
                issue_date_str,
                return_date_str
            ))

            issue_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO "Библиотекарь_выдачи"
                (id_выдачи, id_библиотекаря)
                VALUES (%s, %s)
            """, (issue_id, 1))

            cur.execute("""
                UPDATE "Экземпляр"
                SET статус = 'Выдан'
                WHERE "инвентарный_номер" = %s
            """, (inv_val,))

            conn.commit()

            messagebox.showinfo("Успех", f"Экземпляр {inv_val} успешно выдан")

            for item in tree.get_children():
                tree.delete(item)

            tree.insert("", tk.END, values=(
                ticket_val,
                inv_val,
                "Выдан",
                issue_date_str,
                return_date_str
            ))

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            conn.close()

    win = tk.Toplevel()
    win.title("Оформление комплекта выдачи")
    win.geometry("520x380")

    frame = tk.Frame(win)
    frame.pack(pady=10)

    tk.Label(frame, text="№ читательского билета").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    ticket = tk.Entry(frame)
    ticket.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame, text="Инвентарный номер").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    inv = tk.Entry(frame)
    inv.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame, text="Дата выдачи (дд.мм.гггг)").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    issue_date = tk.Entry(frame)
    issue_date.grid(row=2, column=1, padx=5, pady=5)

    tk.Button(frame, text="Оформить", width=20, command=save)\
        .grid(row=3, column=0, columnspan=2, pady=10)

    columns = ("ticket", "inv", "status", "issue", "return")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    headers = ["№ билета", "Инв. №", "Статус", "Дата выдачи", "Дата сдачи"]
    for col, header in zip(columns, headers):
        tree.heading(col, text=header)
        tree.column(col, width=100, anchor=tk.CENTER)

# редактировать выдачу
def edit_issue():
    def load_issues():
        ticket_val = ticket_entry.get().strip()

        if not ticket_val:
            messagebox.showwarning("Ошибка", "Необходимо ввести номер читательского билета")
            return

        if not ticket_val.isdigit() or len(ticket_val) != 4:
            messagebox.showerror("Ошибка", "Номер билета должен состоять из 4 цифр")
            return

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1 FROM "Читательский_билет"
            WHERE "номер_читательского_билета" = %s
        """, (ticket_val,))
        if not cur.fetchone():
            messagebox.showerror("Ошибка", "Читательский билет не найден")
            conn.close()
            return

        cur.execute("""
            SELECT id_выдачи,
                   инвентарный_номер,
                   статус,
                   дата_выдачи,
                   дата_сдачи
            FROM "Комплект_выдачи"
            WHERE номер_читательского_билета = %s
            ORDER BY дата_выдачи DESC
        """, (ticket_val,))

        rows = cur.fetchall()
        conn.close()

        for item in tree.get_children():
            tree.delete(item)

        if not rows:
            messagebox.showinfo("Результат", "Выдач по этому билету нет")
            return

        for row in rows:
            tree.insert("", tk.END, values=row)

    def on_select(event):
        selected = tree.selection()
        if not selected:
            return

        values = tree.item(selected[0], "values")
        issue_id_var.set(values[0])
        inv_var.set(values[1])
        status_combo.set(values[2])
        return_date_entry.delete(0, tk.END)
        if values[4]:
            return_date_entry.insert(0, values[4])

    def update_issue():
        issue_id = issue_id_var.get()
        inv_num = inv_var.get()
        status_val = status_combo.get()
        return_date_val = return_date_entry.get().strip()


        if not issue_id:
            messagebox.showerror("Ошибка", "Выберите выдачу из списка")
            return
        

        if status_val not in ("Выдан", "В наличии"):
            messagebox.showerror("Ошибка", "Некорректный статус")
            return
        
        if not return_date_val:
            messagebox.showwarning("Ошибка", "Дата сдачи обязательна для заполнения")
            return

        if return_date_val:
            try:
                return_date_dt = datetime.strptime(return_date_val, "%d.%m.%Y")
            except ValueError:
                messagebox.showerror("Ошибка", "Дата сдачи должна быть в формате дд.мм.гггг")
                return
        else:
            return_date_dt = None

        selected = tree.selection()
        if selected:
            values = tree.item(selected[0], "values")
            issue_date_str = values[3]
            issue_date_dt = datetime.strptime(issue_date_str, "%d.%m.%Y")
        else:
            messagebox.showerror("Ошибка", "Не выбрана выдача для редактирования")
            return

        if return_date_dt and return_date_dt < issue_date_dt:
            messagebox.showerror("Ошибка", "Дата сдачи не может быть раньше даты выдачи")
            return

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                UPDATE "Комплект_выдачи"
                SET статус = %s,
                    дата_сдачи = %s
                WHERE id_выдачи = %s
            """, (status_val, return_date_val or None, issue_id))

            cur.execute("""
                UPDATE "Экземпляр"
                SET статус = %s
                WHERE инвентарный_номер = %s
            """, (status_val, inv_num))

            conn.commit()
            messagebox.showinfo("Успех", "Выдача успешно обновлена")
            load_issues()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Ошибка БД", str(e))
        finally:
            conn.close()

    win = tk.Toplevel()
    win.title("Редактирование комплекта выдачи")
    win.geometry("950x500")

    top = tk.Frame(win)
    top.pack(pady=10)

    tk.Label(top, text="№ читательского билета").grid(row=0, column=0, padx=5)
    ticket_entry = tk.Entry(top, width=10)
    ticket_entry.grid(row=0, column=1, padx=5)

    tk.Button(top, text="Показать", command=load_issues)\
        .grid(row=0, column=2, padx=10)

    columns = ("id", "inv", "status", "date_out", "date_in")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True, pady=10)

    headers = ["ID", "Инв. №", "Статус", "Дата выдачи", "Дата сдачи"]
    for col, header in zip(columns, headers):
        tree.heading(col, text=header)
        tree.column(col, width=150, anchor=tk.CENTER)

    tree.bind("<<TreeviewSelect>>", on_select)

    bottom = tk.Frame(win)
    bottom.pack(pady=10)

    issue_id_var = tk.StringVar()
    inv_var = tk.StringVar()

    tk.Label(bottom, text="Статус").grid(row=0, column=0, padx=5)
    status_combo = ttk.Combobox(
        bottom,
        values=["Выдан", "В наличии"],
        state="readonly",
        width=15
    )
    status_combo.grid(row=0, column=1, padx=5)

    tk.Label(bottom, text="Дата сдачи (дд.мм.гггг)").grid(row=0, column=2, padx=5)
    return_date_entry = tk.Entry(bottom, width=15)
    return_date_entry.grid(row=0, column=3, padx=5)

    tk.Button(
        bottom,
        text="Сохранить изменения",
        width=25,
        command=update_issue
    ).grid(row=0, column=4, padx=10)

# смотреть выдачи
def view_issues():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            номер_читательского_билета,
            инвентарный_номер,
            статус,
            дата_выдачи,
            дата_сдачи
        FROM Комплект_выдачи
        ORDER BY дата_выдачи DESC
    """)

    rows = cur.fetchall()
    conn.close()

    win = tk.Toplevel()
    win.title("Список комплектов выдачи")
    win.geometry("900x400")

    columns = (
        "ticket", "inv", "status", "date_out", "date_in"
    )

    tree = ttk.Treeview(win, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    headers = [
        "№ читательского билета",
        "Инвентарный №",
        "Статус",
        "Дата выдачи",
        "Дата сдачи"
    ]

    for col, header in zip(columns, headers):
        tree.heading(col, text=header)
        tree.column(col, width=170, anchor=tk.CENTER)

    for row in rows:
        tree.insert("", tk.END, values=row)