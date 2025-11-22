import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(API_TOKEN)
dp = Dispatcher()

user_lang = {}
user_history = {}  


def translate_text(text, target):
    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except Exception as e:
        return f"Ошибка перевода: {e}"


@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    user_lang[msg.from_user.id] = "en"
    user_history[msg.from_user.id] = []
    await msg.answer(
        "Привет. Я — TranslateMasterBot.\n"
        "Напиши текст — я переведу.\n"
        "Сменить язык: /lang\n"
        "История: /history\n"
        "Очистить историю: /clearhistory"
    )


@dp.message(Command("lang"))
async def lang_cmd(msg: types.Message):
    kb = InlineKeyboardBuilder()

    languages = {
        "en": "Английский",
        "ru": "Русский",
        "uz": "Узбекский",
        "de": "Немецкий",
        "fr": "Французский",
        "es": "Испанский"
    }

    for code, name in languages.items():
        kb.button(text=name, callback_data=f"set_{code}")

    kb.adjust(2)
    await msg.answer("Выбери язык перевода:", reply_markup=kb.as_markup())


@dp.callback_query(lambda c: c.data.startswith("set_"))
async def set_language(c: types.CallbackQuery):
    lang = c.data.replace("set_", "")
    user_lang[c.from_user.id] = lang
    await c.message.edit_text(f"Язык перевода установлен: {lang.upper()}")
    await c.answer()


@dp.message(Command("check"))
async def check_cmd(msg: types.Message):
    try:
        text = msg.text.replace("/check", "").strip()

        if "=" not in text:
            await msg.answer("Используй формат:\n/check слово = перевод")
            return

        left, right = text.split("=", 1)
        left = left.strip()
        right = right.strip()

        correct = GoogleTranslator(source="auto", target="en").translate(left)

        if correct.lower().strip() == right.lower().strip():
            await msg.answer("Верно.")
        else:
            await msg.answer(
                f"Неверно.\nПравильно: {correct.lower().strip()}\n"
                f"Ты написал(а): {right.lower().strip()}"
            )

    except Exception as e:
        await msg.answer(f"Ошибка проверки: {e}")


@dp.message(Command("history"))
async def history_cmd(msg: types.Message):
    user_id = msg.from_user.id

    if user_id not in user_history or len(user_history[user_id]) == 0:
        await msg.answer("История пуста.")
        return

    text = "Последние переводы:\n\n"
    for item in user_history[user_id][-10:]:
        text += f"{item}\n"

    await msg.answer(text)


@dp.message(Command("clearhistory"))
async def clear_history_cmd(msg: types.Message):
    user_id = msg.from_user.id
    user_history[user_id] = []
    await msg.answer("История очищена.")


@dp.message()
async def translate_msg(msg: types.Message):
    user_id = msg.from_user.id
    lang = user_lang.get(user_id, "en")

    result = translate_text(msg.text, lang)

  
    if user_id not in user_history:
        user_history[user_id] = []

    user_history[user_id].append(f"{msg.text} → {result}")

    await msg.answer(f"Перевод ({lang.upper()}):\n{result}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())




