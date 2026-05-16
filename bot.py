import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Привет! Я учебный бот\n\n"
        "📌 Волков Родион\n\n"
        "Я могу помочь тебе с учебой:\n"
        "/help — список команд\n"
        "/math — мини тест по математике\n"
        "/info — что я умею\n"
        "/ask — задать учебный вопрос (пример: /ask что такое Python)"
    )


@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "📚 Команды:\n\n"
        "/math — мини тест\n"
        "/info — возможности бота\n"
        "/ask <вопрос> — задать вопрос\n"
    )


@dp.message(Command("info"))
async def info(message: Message):
    await message.answer(
        "🤖 Я учебный бот Волков Родион\n\n"
        "Помогаю с:\n"
        "- программированием\n"
        "- школьными предметами\n"
        "- тестами\n"
        "- объяснениями тем простым языком"
    )


@dp.message(Command("ask"))
async def ask(message: Message):
    text = message.text.replace("/ask", "").strip()

    if not text:
        await message.answer("Напиши вопрос после команды:\n/ask что такое алгоритм")
        return

    if "python" in text.lower():
        await message.answer("Python — это язык программирования для создания программ, сайтов и ботов.")
    elif "алгоритм" in text.lower():
        await message.answer("Алгоритм — это последовательность шагов для решения задачи.")
    else:
        await message.answer("Я пока не знаю ответ, но могу помочь с Python и базовыми темами.")


@dp.message(Command("math"))
async def math_test(message: Message):
    await message.answer(
        "🧠 Мини тест:\n\n"
        "Сколько будет 7 × 8?\n"
        "Ответ напиши сообщением."
    )


@dp.message()
async def check_answer(message: Message):
    if message.text and message.text.isdigit():
        if message.text == "56":
            await message.answer("✅ Правильно!")
        else:
            await message.answer("❌ Неправильно, попробуй ещё раз.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
if __name__ == "__main__":
    asyncio.run(main())
