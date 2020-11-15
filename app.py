from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms import validators
import json
import random

app = Flask(__name__)
app.secret_key = "uZM3KBTnEFXZfCFmzGdgLeYQwRjMD6INp4C0JiO1VHy9LXYsdv"

"""Загрузка данных из JSON-файлов
Данные записанны были с помощью доработанного файла data.py
"""
with open("teachers.json") as f:
    teachers = json.load(f)

with open("goals.json") as f:
    goals = json.load(f)

# Словарь, хранящий имена дней недели
days = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница",
        "sat": "Суббота", "sun": "Воскресенье"}


# Запись заявок на подбор преподавателя в JSON-файл request.json
def update_requests(goal, free, name, phone):
    with open("request.json", "r") as f:
        requests = json.load(f)
    requests.append({"goal": goal, "free": free, "name": name, "phone": phone})
    with open("request.json", "w") as f:
        json.dump(requests, f)


# Запись заявок на подбор преподавателя в JSON-файл request.json
def update_bookings(teacher_id, name, phone, weekday, time):
    with open("booking.json", "r") as f:
        requests = json.load(f)
    requests.append({"teacher_id": teacher_id, "name": name, "phone": phone, "weekday": weekday, "time": time})
    with open("booking.json", "w") as f:
        json.dump(requests, f)


class RequestForm(FlaskForm):
    goals_list = []
    for goal, name in goals.items():
        goals_list.append((goal, name[2:]))
    goal = RadioField("Какая цель занятий?", choices=goals_list,
                      validators=[validators.InputRequired("Выберите цель занятий!")])
    free = RadioField("Сколько времени есть?", choices=[("1-2 часа в неделю", "1-2 часа в неделю"),
                                                        ("3-5 часов в неделю", "3-5 часов в неделю"),
                                                        ("5-7 часов в неделю", "5-7 часов в неделю"),
                                                        ("7-10 часов в неделю", "7-10 часов в неделю")],
                      validators=[validators.InputRequired("Выберите свободное время!")])
    name = StringField("Вас зовут", validators=[validators.InputRequired("Введите своё имя!"),
                                                validators.length(min=3, message="Имя не может быть меньше 3 символов!")])
    phone = StringField("Ваш телефон", validators=[validators.InputRequired("Введите свой номер!"),
                                                   validators.regexp(
                                                       "^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$",
                                                       message="Вы ввели некорректный номер телефона!")])


class BookingForm(FlaskForm):
    clientName = StringField("Вас зовут", validators=[validators.InputRequired("Введите своё имя!"),
                                                      validators.length(min=3,
                                                                        message="Имя не может быть меньше 3 символов!")])
    clientPhone = StringField("Ваш телефон", validators=[validators.InputRequired("Введите свой номер!"),
                                                         validators.regexp(
                                                             "^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$",
                                                             message="Вы ввели некорректный номер телефона!")])


@app.route("/")
def index_view():
    teachers_random = teachers
    random.shuffle(teachers_random)
    return render_template("index.html", goals=goals, teachers=teachers_random[:6])


@app.route("/all/")
def all_view():
    return render_template("index.html", goals=goals, teachers=teachers)


@app.route("/goal/<goal>/")
def goal_view(goal):
    teachers_goal = []
    for teacher in teachers:
        if goal in teacher["goals"]:
            teachers_goal.append(teacher)
    return render_template("goal.html", goals=goals, goal=goal, teachers=teachers_goal)


@app.route("/profile/<int:teacher_id>/")
def profile_view(teacher_id):
    teacher = []
    for x in teachers:
        if x["id"] == teacher_id:
            teacher = x
    return render_template("profile.html", days=days, goals=goals, teacher=teacher)


@app.route("/request/", methods=["GET", "POST"])
def request_view():
    form = RequestForm()
    if request.method == "POST":
        if form.validate_on_submit():
            goal = goals[form.goal.data][2:]
            free = form.free.data
            name = form.name.data
            phone = form.phone.data
            update_requests(goal, free, name, phone)
            return render_template("request_done.html", goal=goal, free=free, name=name, phone=phone)
    return render_template("request.html", form=form)


@app.route("/booking/<time>/<day>/<int:teacher_id>/", methods=["GET", "POST"])
def booking_view(time, day, teacher_id):
    # Приводим время, переданное в скрытом запросе обратно к виду XX:XX или X:XX
    # Возможно есть способ попроще, регулярные выражения точно бы помогли
    if len(time) == 3:
        time = time.replace("00", ":00")
    else:
        time = time[:2] + time[2:].replace("00", ":00")
    # Добываем имя преподавателя
    for x in teachers:
        if x["id"] == teacher_id:
            teacher_name = x["name"]
    form = BookingForm()
    if request.method == "POST":
        if form.validate_on_submit():
            clientName = form.clientName.data
            clientPhone = form.clientPhone.data
            update_bookings(teacher_id, clientName, clientPhone, day, time)
            return render_template("booking_done.html", clientName=clientName, clientPhone=clientPhone,
                                   clientWeekday=days[day], clientTime=time)
    return render_template("booking.html", form=form, day=day, dayname=days[day], time=time, teacher_id=teacher_id,
                           teacher_name=teacher_name)


if __name__ == '__main__':
    app.run()
