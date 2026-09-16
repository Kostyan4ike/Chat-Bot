from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import BOT_TOKEN, DATABASE_URL, ADMIN_IDS
from database import Database
import asyncio

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database(DATABASE_URL)

async def main():
    await db.connect()
    await db.create_table()
    await dp.start_polling(bot)
    

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

class FilmDialog(StatesGroup):
    predstart = State()
    sign = State()
    main = State()
    profile = State()
    edit_phone = State()
    change_balance = State()
    start = State()
    genre = State()
    select = State()

genres = [
            "Боевик",
            "Фантастика",
            "Драма",
            "Научное"
          ]

@dp.message(CommandStart())
async def start_command(message: Message, state: FSMContext):

    await state.set_state(FilmDialog.start)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Начать", callback_data="Go"),
                InlineKeyboardButton(text="Не интересно", callback_data="No")
            ]
        ]
    )
    await message.answer(
        "   Привет! Я бот с базой данных о популярных фильмах. Я могу посоветовать тебе фильм исходя из твоих предпочтений.\n" \
        "   Тебе интересно это? ",
        reply_markup = keyboard
    )

#Начинаем
@dp.callback_query(FilmDialog.start, F.data == 'Go')
async def Lets_Go(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FilmDialog.predstart)
    user_id = callback.from_user.id
    if await db.is_registered(user_id):
        phone = await db.get_phone(user_id)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text = "Да"),
                ]
            ]
        )
        await callback.message.answer("Я вижу вы уже ранее регистрировались в системе, это ваш телефон? \n" \
        f"{phone}\n Если нет, напишите пожалуйста свой телефон в формате +71231231212"
        , reply_markup=keyboard)
        await callback.answer()

    else:
        contact_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="📱 Поделиться контактом",
                        request_contact=True
                    )
                ]
            ],
            resize_keyboard=True
        )
        await callback.message.answer(
            "Вам нужно пройти регистрацию, для этого нажмите на кнопку",
            reply_markup=contact_keyboard
        )
        await callback.answer()

# Переход в подтверждение   
@dp.message(FilmDialog.predstart, F.text == "Да")
async def conf(message: Message, state: FSMContext):    
    await state.set_state(FilmDialog.sign)
    keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Ура!")
                ]
            ]
        )
    await message.answer("Отлично, продолжаем!", reply_markup=keyboard)
#Изменение + переход в подтверждение
@dp.message(FilmDialog.predstart, F.text)
async def edit(message: Message, state: FSMContext):
    new_phone = message.text
    user_id = message.from_user.id
    await db.edit_phone(user_id, new_phone)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Ура!")
            ]
        ]
    )
    await message.answer("Телефон успешно изменен!", reply_markup=keyboard)
    await state.set_state(FilmDialog.sign)

#Добавили контакт
@dp.message(FilmDialog.predstart, F.contact)
async def phone_received(message: Message, state: FSMContext):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    await db.add_contact(user_id, phone)
    keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Ура!")
                ]
            ]
        )
    await message.answer(
        f"Ваш номер {phone} сохранен! Вы зарегестрировались!",reply_markup=keyboard
    )
    await state.set_state(FilmDialog.sign)

# Вошли в систему
@dp.message(FilmDialog.sign, F.text)
async def info(message: Message, state: FSMContext):
    await state.set_state(FilmDialog.main)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Профиль"),
                KeyboardButton(text="Перейти к каталогу")
            ]
        ]
    )
    await message.answer("Вы вошли в систему! Далее вы можете перейти к каталогу фильмов либо перейти в профиль",reply_markup=keyboard)
# Перешли в профиль 
@dp.message(FilmDialog.main, F.text == "Профиль")
async def profile(message: Message, state: FSMContext):
    await state.set_state(FilmDialog.profile)
    user_id = message.from_user.id 
    info = await db.get_profile(user_id)
    id = info['user_id']
    phone = info['phone']
    balance = info['balance']
    keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Сменить номер телефона"),
                    KeyboardButton(text="Пополнить баланс"),
                    KeyboardButton(text="Назад")
                ]
            ]
        )
    await message.answer(
        "Вот данные по вашему профилю.\n" \
        f"ID: {id}\n" \
        f"Телефон: {phone}\n" \
        f"Баланс: {balance}\n", reply_markup=keyboard
    )
# Ветки профиля
@dp.message(FilmDialog.profile, F.text == "Назад")
async def back(message: Message, state: FSMContext):
    await state.set_state(FilmDialog.main)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Профиль"),
                KeyboardButton(text="Перейти к каталогу")
            ]
        ]
    )
    await message.answer("Вы вернулись в меню! Далее вы можете перейти к каталогу фильмов либо перейти в профиль",reply_markup=keyboard)

@dp.message(FilmDialog.profile, F.text == "Сменить номер телефона")
async def edit(message: Message, state: FSMContext):
    await message.answer("Напишите ваш актуальный номер телефона")
    await state.set_state(FilmDialog.edit_phone)

@dp.message(FilmDialog.edit_phone, F.text)
async def edit(message: Message, state: FSMContext):
    new_phone = message.text
    user_id = message.from_user.id
    await db.edit_phone(user_id, new_phone)
    await state.set_state(FilmDialog.profile)
    user_id = message.from_user.id 
    info = await db.get_profile(user_id)
    id = info['user_id']
    phone = info['phone']
    balance = info['balance']
    keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Сменить номер телефона"),
                    KeyboardButton(text="Пополнить баланс"),
                    KeyboardButton(text="Назад")
                ]
            ]
        )
    await message.answer(
        "Вот данные по вашему профилю.\n" \
        f"ID: {id}\n" \
        f"Телефон: {phone}\n" \
        f"Баланс: {balance}\n", reply_markup=keyboard
    )

@dp.message(FilmDialog.profile, F.text == "Пополнить баланс")
async def balance(message: Message, state: FSMContext):
    await state.set_state(FilmDialog.change_balance)
    await message.answer("Напишите насколько хотите пополнить баланс")

@dp.message(FilmDialog.change_balance, F.text)
async def change_balance(message: Message, state: FSMContext):
    user_id = message.from_user.id
    old_balance = await db.get_balance(user_id)
    old_balance = int(old_balance['balance'])
    sum = int(message.text)
    result = old_balance + sum
    await db.change_balance(user_id, int(result))
    await state.set_state(FilmDialog.profile)
    user_id = message.from_user.id 
    info = await db.get_profile(user_id)
    id = info['user_id']
    phone = info['phone']
    balance = info['balance']
    keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Сменить номер телефона"),
                    KeyboardButton(text="Пополнить баланс"),
                    KeyboardButton(text="Назад")
                ]
            ]
        )
    await message.answer(
        "Вот данные по вашему профилю.\n" \
        f"ID: {id}\n" \
        f"Телефон: {phone}\n" \
        f"Баланс: {balance}\n", reply_markup=keyboard
    )

# Переход к каталогу

@dp.message(FilmDialog.main, F.text == 'Перейти к каталогу')
async def cataloge(message: Message, state:FSMContext):
    await state.set_state(FilmDialog.genre)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Боевик"),
                KeyboardButton(text="Фантастика"),
                KeyboardButton(text="Драма"),
                KeyboardButton(text= "Научное"),
                KeyboardButton(text="Назад")
            ]
        ]
    )
    await message.answer('Отлично, давайте определимся с жанром:', reply_markup = keyboard)
    #await message.edit_text('')

# Назад
@dp.message(FilmDialog.genre, F.text.lower() == "назад")
async def back(message:Message, state:FSMContext):
    await state.set_state(FilmDialog.main)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Профиль"),
                KeyboardButton(text="Перейти к каталогу")
            ]
        ]
    )
    await message.answer("Вы вернулись в главное меню! Далее вы можете перейти к каталогу фильмов либо перейти в профиль",reply_markup=keyboard)

@dp.message(FilmDialog.genre, F.text.in_(genres))
async def select(message:Message, state:FSMContext):
    await state.set_state(FilmDialog.select)
    films = await db.find_film(message.text)
    result = "Найдены следующие фильмы, выберите какой фильм вы бы хотели посмотреть и напишите его название:\n" + "\n".join(films)
    await message.answer(result, reply_markup = ReplyKeyboardRemove())



@dp.message(FilmDialog.select, F.text)
async def select(message:Message, state:FSMContext):
    user_id = message.from_user.id
    info = await db.select_film(message.text)
    cost = int(info['cost'])
    balance = await db.get_balance(user_id)
    balance = int(balance['balance'])
    if balance > cost:
        await db.change_balance(user_id, balance - cost)
        await message.answer(
            f"Отлично, c вашего счета было списано {info['cost']}, теперь у вас на балансе {balance - cost}\n" \
            f"Вот полная информация о фильме:\n" \
            f"Название: {info['title']}\n" \
            f"Жанр: {info['genre']}\n" \
            f"Год: {info['year']}\n" \
            f"Описание: {info['description']}\n" \
            f"Ссылка: {info['url']}\n" \
            )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Профиль")
                ]
            ]
        )
        await state.set_state(FilmDialog.main)
        await message.answer(" На вашем счету не достаточно средств, пополните кошелек в профиле", reply_markup=keyboard)



















if __name__ == "__main__":
    asyncio.run(main())