import sqlite3
import re
from tkinter import Tk, ttk, Listbox, Text, messagebox, Toplevel, END
from datetime import datetime
from dateutil import parser
# Создание соединения с БД
connect = sqlite3.connect('tasks.db')
cursor = connect.cursor()

# Создание таблицы задач, если её нет
cursor.execute('''CREATE TABLE IF NOT EXISTS Tasks (
             id INTEGER PRIMARY KEY,
             Name TEXT NOT NULL,
             Description TEXT,
             Assignee TEXT NOT NULL,
             Deadline TEXT NOT NULL,
             status TEXT)''')
connect.commit()

# Функция для добавления задачи в БД
def Create_Task(name, description, assignee, deadline):
    cursor.execute("INSERT INTO tasks (Name, Description, Assignee, Deadline, Status) VALUES (?, ?, ?, ?, 'Active')",
              (name, description, assignee, deadline))
    connect.commit()

# Функция для получения списка задач из БД
def Get_Tasks():
    cursor.execute("SELECT * FROM tasks")
    return cursor.fetchall()

# Функция для отметки задачи как выполненной
def Task_Complete(task_id):
    cursor.execute("UPDATE tasks SET status='Выполнено' WHERE id=?", (task_id,))
    connect.commit()

# Функция для отметки задачи как невыполненной
def Task_Failed(task_id):
    cursor.execute("UPDATE tasks SET status='Провалено' WHERE id=?", (task_id,))
    connect.commit()

# Функция для удаления задачи из БД
def Delete_Task(task_id):
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    connect.commit()

# Функция обновления списка задач
def Refresh_Listbox(listbox):
    Check_Deadlines()
    listbox.delete(0, END)
    tasks = Get_Tasks()
    for task in tasks:
        listbox.insert(END, task[1])

# Функция проверки дедлайнов задач:
def Check_Deadlines():
    current_date = datetime.now().strftime('%d.%m.%Y')
    tasks = Get_Tasks()
    for task in tasks:
        task_id, deadline, status = task[0], task[4], task[5]
        if status != 'Выполнено' and datetime.strptime(deadline, '%d.%m.%Y') < datetime.strptime(current_date, '%d.%m.%Y'):
            Task_Failed(task_id)
# Функция создания окна для создания задачи
def Create_Task_Window(listbox):

    #  Функция создания задачи в интерфейсе
    def Save_Task():
        name = name_entry.get()
        description = description_entry.get("1.0", END).strip()
        assignee = assignee_entry.get()
        deadline = deadline_entry.get()


        # Проверка правильности написания ФИО исполнителя
        if not assignee or not re.match(r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.[А-ЯЁ]\.$|^[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+$', assignee):
            messagebox.showerror("Ошибка", "Исполнитель должен быть введён или в формате 'Фамилия Имя Отчество', или в формате 'Фамилия Инициалы'")
            assignee_entry.delete(0, END)
            return

        # Проверка правильности написания даты дедлайна
        try:
            parsed_date = parser.parse(deadline)
            deadline = parsed_date.strftime('%d.%m.%Y')
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты. Введите корректную дату.")
            return

        Create_Task(name, description, assignee, deadline)
        create_window.destroy()
        Refresh_Listbox(listbox)
        Check_Deadlines()

    # Создание кнопок меню
    create_window = Toplevel()
    create_window.title("Создать задачу")

    padding = {'padx': 10, 'pady': 5}

    name_label = ttk.Label(create_window, text="Название задачи:")
    name_label.grid(row=0, column=0, **padding)
    name_entry = ttk.Entry(create_window, width=40)
    name_entry.grid(row=0, column=1, **padding)

    description_label = ttk.Label(create_window, text="Описание задачи:")
    description_label.grid(row=1, column=0, **padding, sticky="w")
    description_entry = Text(create_window, width=40, height=5)
    description_entry.grid(row=1, column=1, **padding)

    assignee_label = ttk.Label(create_window, text="Исполнитель задачи:")
    assignee_label.grid(row=2, column=0, **padding)
    assignee_entry = ttk.Entry(create_window, width=40)
    assignee_entry.grid(row=2, column=1, **padding)

    deadline_label = ttk.Label(create_window, text="Дедлайн задачи:")
    deadline_label.grid(row=3, column=0, **padding)
    deadline_entry = ttk.Entry(create_window, width=40)
    deadline_entry.grid(row=3, column=1, **padding)

    save_button = ttk.Button(create_window, text="Сохранить", command=Save_Task)
    save_button.grid(row=4, column=0, columnspan=2, pady=10)



# основная функция
def main():
    root = Tk()
    root.title("Task Manager")

    style = ttk.Style()
    style.theme_use('clam')

    font = ("Helvetica", 12)
    label_style = {"anchor": "w", "font": font,  "background": "#f5f5f5", "wraplength": 400}

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill="both", expand=True)

    label = ttk.Label(main_frame, text="Задачи:")
    label.grid(row=0, column=0, sticky="w")

    listbox = Listbox(main_frame, width=50, height=20)
    listbox.grid(row=1, column=0, rowspan=6, sticky="nsew")

    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=listbox.yview)
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=1, column=1, rowspan=6, sticky="ns")

    tasks = Get_Tasks()
    for task in tasks:
        listbox.insert(END, task[1])

    def Refresh_List():
        Refresh_Listbox(listbox)

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=1, column=2, rowspan=6, padx=10, sticky="ns")

    create_button = ttk.Button(button_frame, text="Создать задачу", command=lambda: Create_Task_Window(listbox))
    create_button.pack(pady=5)

    refresh_button = ttk.Button(button_frame, text="Обновить задачи", command=Refresh_List)
    refresh_button.pack(pady=5)


    def Show_Info_Button():
        tasks = Get_Tasks()
        selected_task = listbox.curselection()
        if selected_task:
            task_id = tasks[selected_task[0]][0]
            task_info_window = Toplevel(root)
            task_info_window.title("Информация о задаче")
            task_info_window.configure(bg="#f5f5f5")

            task_info_frame = ttk.Frame(task_info_window, padding="10")
            task_info_frame.pack(fill="both", expand=True)

            cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
            task = cursor.fetchone()

            label_style = {"anchor": "w", "font": font,  "background": "#f5f5f5", "wraplength": 400}

            task_info_label = ttk.Label(task_info_frame, text=f"Название: {task[1]}", **label_style)
            task_info_label.grid(row=0, column=0, sticky="w", pady=5)

            task_info_label = ttk.Label(task_info_frame, text=f"Описание: {task[2]}", **label_style)
            task_info_label.grid(row=1, column=0, sticky="w", pady=5)

            task_info_label = ttk.Label(task_info_frame, text=f"Исполнитель: {task[3]}", **label_style)
            task_info_label.grid(row=2, column=0, sticky="w", pady=5)

            task_info_label = ttk.Label(task_info_frame, text=f"Дедлайн: {task[4]}", **label_style)
            task_info_label.grid(row=3, column=0, sticky="w", pady=5)

            task_info_label = ttk.Label(task_info_frame, text=f"Статус: {task[5]}", **label_style)
            task_info_label.grid(row=4, column=0, sticky="w", pady=5)

    show_info_button = ttk.Button(button_frame, text="Показать информацию о задаче", command=Show_Info_Button)
    show_info_button.pack(pady=5)

    def Complete_Task_Button():
        tasks = Get_Tasks()
        selected_task = listbox.curselection()
        if selected_task:
            task_id = tasks[selected_task[0]][0]
            Task_Complete(task_id)
            Refresh_Listbox(listbox)
            Check_Deadlines()

    def Fail_Task_Button():
        tasks = Get_Tasks()
        selected_task = listbox.curselection()
        if selected_task:
            task_id = tasks[selected_task[0]][0]
            Task_Failed(task_id)
            Refresh_Listbox(listbox)
            Check_Deadlines()



    def Delete_Task_Button():
        tasks = Get_Tasks()
        selected_task = listbox.curselection()
        if selected_task:
            task_id = tasks[selected_task[0]][0]
            Delete_Task(task_id)
            Refresh_Listbox(listbox)
            Check_Deadlines()



    complete_button = ttk.Button(button_frame, text="Пометить как 'Выполнено'", command=Complete_Task_Button)
    complete_button.pack(pady=5)

    fail_button = ttk.Button(button_frame, text="Пометить как 'Провалено'", command=Fail_Task_Button)
    fail_button.pack(pady=5)

    delete_button = ttk.Button(button_frame, text="Удалить задачу", command=Delete_Task_Button)
    delete_button.pack(pady=5)

    Check_Deadlines()
    root.mainloop()

main()
