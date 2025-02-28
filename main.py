import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

TOKEN = ""
ADMINS = [
]
dp = Dispatcher()
bot = Bot(TOKEN)


class StatesMessage(StatesGroup):
    msg = State()
    admin_msg = State()


def send_message_user(user_id: int):
    _ = InlineKeyboardBuilder()
    _.row(
        InlineKeyboardButton(text="Ответить", callback_data=f"send_msg:{user_id}")
    )
    return _.as_markup()


@dp.message(CommandStart())
async def echo_handler(message: types.Message, state: FSMContext):
    text = f"""
Приветствую, {message.from_user.username}! Напишите ваш вопрос и мы ответим Вам в ближайшее время.    
"""
    await message.answer(text)
    await state.set_state(StatesMessage.msg)


@dp.message(StatesMessage.msg)
async def message(message: types.Message):
    text = message.text
    for admin in ADMINS:
        await bot.send_message(admin, f"Пришло сообщение от пользователя: @{message.from_user.username}\n\n{text}",
                               reply_markup=send_message_user(message.from_user.id))

    await message.answer("Ожидайте. Вам скоро ответят")


@dp.callback_query(F.data.contains("send_msg:"))
async def message(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id in ADMINS:
        user_id = call.data.split(":")[-1]
        await state.update_data({"user_id": user_id})
        await call.message.answer(f"Отправьте сообщение пользователю {user_id}:")
        await state.set_state(StatesMessage.admin_msg)


@dp.message(StatesMessage.admin_msg)
async def message(message: types.Message, state: FSMContext):
    user_id = (await state.get_data())["user_id"]
    text = message.text
    await bot.send_message(user_id, text)
    await message.answer("Успешно отправлено")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
