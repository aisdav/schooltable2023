import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import pdfkit
import os
import datetime
from config import TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

def connect_db():
    connection = sqlite3.connect('school1.db')
    cursor = connection.cursor()
    return connection, cursor

async def start_handler(message: types.Message):
    classes = get_classes()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for class_name in classes:
        keyboard
async def start_handler(message: types.Message):
    classes = get_classes()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for class_name in classes:
        keyboard.add(class_name)
    await message.answer("Выберите класс:", reply_markup=keyboard)
    await States.waiting_for_class.set()


async def class_chosen_handler(message: types.Message, state: FSMContext):
    class_name = message.text
    students = get_students(class_name)
    await message.answer(f"Первый ученик: {students[0]}\nПрисутствует?", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Да", "Нет"))
    await state.update_data(students=students, index=0, class_name=class_name)
    await States.waiting_for_att.set()

async def att_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    students = data.get('students')
    index = data.get('index')
    class_name = data.get('class_name')
    name = students[index]
    att = message.text
    update_att(name, att)
    if index == len(students)-1:
        file_name = generate_pdf(class_name)
        await bot.send_document(832892390, open(file_name, "rb"))
        os.remove(file_name)
        await message.answer("Отчет отправлен завучу!")
        await state.finish()
    else:
        index += 1
        await message.answer(f"Следующий ученик: {students[index]}\nПрисутствует?", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Да", "Нет"))
        await state.update_data(students=students, index=index, class_name=class_name)
        await States.waiting_for_att.set()
def generate_pdf(class_name):
    connection, cursor = connect_db()
    cursor.execute("SELECT name, att FROM students WHERE class=?", (class_name,))
    rows = cursor.fetchall()
    html = "<table><tr><th>Имя</th><th>Посещение</th></tr>"
    for row in rows:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td></tr>"
    html += "</table>"
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Формируем имя файла с помощью текущей даты/времени и названия класса
    file_name = f"{now}_{class_name}.pdf"
    pdfkit.from_string(html,file_name, options={'encoding': "UTF-8"})
    connection.close()
    return file_name

def update_att(name: str, att: str):
    connection, cursor = connect_db()
    cursor.execute("UPDATE students SET att = ? WHERE name = ?", (att, name))
    connection.commit()
    connection.close()
def get_students(class_name):
    connection, cursor = connect_db()
    cursor.execute(f"SELECT name FROM students WHERE class='{class_name}'")
    students = [item[0] for item in cursor.fetchall()]
    connection.close()
    return students
class States(StatesGroup):
    waiting_for_class = State()
    waiting_for_name = State()
    waiting_for_att = State()
def get_classes():
    connection, cursor = connect_db()
    cursor.execute("SELECT DISTINCT class FROM students")
    classes = [item[0] for item in cursor.fetchall()]
    connection.close()
    return classes
dp.register_message_handler(start_handler, state=None)
dp.register_message_handler(class_chosen_handler, state=States.waiting_for_class)
dp.register_message_handler(att_handler, state=States.waiting_for_att)
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
