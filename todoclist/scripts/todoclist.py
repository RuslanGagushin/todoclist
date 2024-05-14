import configparser
import os
import typer
from todoist_api_python.api import TodoistAPI
from rich import print
from rich.panel import Panel
from datetime import datetime, timedelta

# Путь к файлу конфигурации
CONFIG_FILE = "docli.ini"


# Функция для чтения и записи токена в файл конфигурации
def update_config(token):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if not config.has_section("Todoist"):
        config.add_section("Todoist")
    config.set("Todoist", "token", token)
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)


# Функция для получения токена из файла конфигурации
def get_token():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if config.has_section("Todoist"):
        return config.get("Todoist", "token")
    return None


TOKEN = get_token()

# Если токен отсутствует в файле конфигурации, запросить его у пользователя
if TOKEN is None:
    print("No token found. Please provide your Todoist API token:")
    TOKEN = input()
    update_config(TOKEN)
app = typer.Typer()


# Initialize the Todoist API object with your API token
api = TodoistAPI(TOKEN)

# get today data
TODAY = str(datetime.today())[0:10]


def get_all_tasks():
    """Function get all tasks from Todoist API and return dict with [id] as a Key
    and tuple of due_date and content"""
    tasks_list = api.get_tasks()
    tasks_dict = {}

    for i in range(len(tasks_list)):
        # Add component to dict [task_id]: (due_date, task_content, datetime)
        tasks_dict[tasks_list[i].id] = (
            tasks_list[i].due.date,
            tasks_list[i].content,
            tasks_list[i].due.datetime,
        )

    for key, value in tasks_dict.items():
        if value[2] is None:
            tasks_dict[key] = (value[0], value[1], "ALL DAY")
        elif value[2]:
            date_time_str = value[2]
            if "T" in date_time_str:
                date, time = date_time_str.split("T")
                if "." in time:
                    time = time.split(".")[0]
                tasks_dict[key] = (value[0], value[1], time[:5])

    return tasks_dict


TASKS_DICT = get_all_tasks()
TASKS_DICT = dict(sorted(TASKS_DICT.items(), key=lambda item: item[1]))

# === Make agenda list function ===


def agenga_date_list():
    """Make a list of date and weekdays for agenda table"""
    # Получаем сегодняшнюю дату
    current_date = datetime.now()

    # Создаем список для хранения результатов
    date_list = []

    # Получаем даты и дни недели на следующие 7 дней
    for _ in range(7):
        # Получаем строковое представление текущей даты
        date_str = current_date.strftime("%Y-%m-%d")
        # Получаем день недели текущей даты
        day_of_week = current_date.strftime("%A")
        # Добавляем пару [date, day of the week] в список
        date_list.append([date_str, day_of_week])
        # Увеличиваем текущую дату на один день
        current_date += timedelta(days=1)
    return date_list


@app.command()
def hello():
    print("Welcome to DoCli - Todoist Cli app")


@app.command()
def today():

    today_tasks = ""

    for key, value in TASKS_DICT.items():
        task_line = f" \n {'◉'} {TASKS_DICT[key][2]} -- {TASKS_DICT[key][1]}"
        if TASKS_DICT[key][0] == TODAY:
            today_tasks += task_line
        if today_tasks == "":
            today_tasks = "All done for today"

    print(Panel(today_tasks, title="Today tasks"))


@app.command()
def all():

    all_tasks = ""

    for key, value in TASKS_DICT.items():
        task_line = f" \n {'◉'} {
            TASKS_DICT[key][0]} --{TASKS_DICT[key][2]} -- {TASKS_DICT[key][1]}"
        # print(task_line)
        all_tasks += task_line

    print(Panel(all_tasks, title="All tasks"))


@app.command()
def agenda():
    agenda_list = agenga_date_list()
    agenda = ""

    for d in agenda_list:
        found_task = False
        for key, value in TASKS_DICT.items():
            if TASKS_DICT[key][0] == d[0]:
                task_line = f" \n {'◉'} {TASKS_DICT[key][2]} -- {TASKS_DICT[key][1]}"
                agenda += task_line
                found_task = True
        if not found_task:
            agenda = "No tasks due this day"
        print(Panel(agenda, title=f"{d[0]} -- {d[1]}"))
        agenda = ""


# === ADD NEW TASK ===


@app.command()
def add():
    content = input("What task? ")
    due = input("Due date? ")
    task = api.add_task(content=content, due_string=due)
    print(f"{task.content} added")


if __name__ == "__main__":
    get_all_tasks()
    app()
