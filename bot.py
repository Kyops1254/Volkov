import asyncio
import os
import requests
import aiosqlite

from collections import defaultdict

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from dotenv import load_dotenv

from database import init_db

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB = "study.db"


# =========================
# MEMORY + MODES
# =========================
user_memory = defaultdict(list)
user_mode = defaultdict(lambda: "teacher")

MAX_MEMORY = 6


# =========================
# AI FUNCTION
# =========================
def ask_ai(user_id: int, question: str):

    api_key = os.getenv("DEEPSEEK_API_KEY")

    url = "https://api.deepseek.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": question}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    print("STATUS:", response.status_code)
    print("TEXT:", response.text)

    return response.text

# =========================
# START
# =========================
@dp.message(Command("start"))
async def start(message: Message):

    await message.answer(
        "📚 Учебный бот + ИИ\n\n"
        "Команды:\n"
        "/add_homework subject | task\n"
        "/homework\n"
        "/add_grade subject grade\n"
        "/grades\n"
        "/add_reminder text\n"
        "/reminders\n"
        "/mode teacher/simple/short\n\n"
        "💬 Просто напиши сообщение — я отвечу как ИИ"
    )


# =========================
# MODE
# =========================
@dp.message(Command("mode"))
async def set_mode(message: Message):

    try:
        mode = message.text.split()[1].lower()

        if mode not in ["teacher", "simple", "short"]:
            await message.answer("Режимы: teacher / simple / short")
            return

        user_mode[message.from_user.id] = mode

        await message.answer(f"✅ Режим установлен: {mode}")

    except:
        await message.answer("Пример: /mode teacher")


# =========================
# AI CHAT (OPTIONAL COMMAND)
# =========================
@dp.message(Command("ai"))
async def ai_command(message: Message):

    text = message.text.replace("/ai ", "").strip()

    if not text:
        await message.answer("Напиши вопрос\nПример: /ai что такое интеграл")
        return

    await message.answer("🤖 Думаю...")

    answer = ask_ai(message.from_user.id, text)

    await message.answer(answer)


# =========================
# HOMEWORK
# =========================
@dp.message(Command("add_homework"))
async def add_homework(message: Message):

    try:
        data = message.text.replace("/add_homework ", "")
        subject, task = data.split("|")

        async with aiosqlite.connect(DB) as db:
            await db.execute(
                """
                INSERT INTO homework (user_id,subject,task)
                VALUES(?,?,?)
                """,
                (message.from_user.id, subject.strip(), task.strip())
            )
            await db.commit()

        await message.answer("✅ Домашка добавлена")

    except:
        await message.answer("Пример:\n/add_homework Math | page 10")


@dp.message(Command("homework"))
async def homework(message: Message):

    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            """
            SELECT subject,task
            FROM homework
            WHERE user_id=?
            """,
            (message.from_user.id,)
        )
        rows = await cursor.fetchall()

    if not rows:
        await message.answer("Домашек нет")
        return

    text = "📚 Домашки:\n\n"

    for row in rows:
        text += f"{row[0]} — {row[1]}\n"

    await message.answer(text)


# =========================
# GRADES
# =========================
@dp.message(Command("add_grade"))
async def add_grade(message: Message):

    try:
        args = message.text.split()

        subject = args[1]
        grade = args[2]

        async with aiosqlite.connect(DB) as db:
            await db.execute(
                """
                INSERT INTO grades (user_id,subject,grade)
                VALUES(?,?,?)
                """,
                (message.from_user.id, subject, grade)
            )
            await db.commit()

        await message.answer("✅ Оценка добавлена")

    except:
        await message.answer("Пример:\n/add_grade Math 5")


@dp.message(Command("grades"))
async def grades(message: Message):

    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            """
            SELECT subject,grade
            FROM grades
            WHERE user_id=?
            """,
            (message.from_user.id,)
        )
        rows = await cursor.fetchall()

    if not rows:
        await message.answer("Оценок нет")
        return

    text = "🏆 Оценки:\n\n"

    for row in rows:
        text += f"{row[0]} — {row[1]}\n"

    await message.answer(text)


# =========================
# REMINDERS
# =========================
@dp.message(Command("add_reminder"))
async def add_reminder(message: Message):

    text = message.text.replace("/add_reminder ", "")

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            INSERT INTO reminders (user_id,text)
            VALUES(?,?)
            """,
            (message.from_user.id, text)
        )
        await db.commit()

    await message.answer("✅ Напоминание добавлено")


@dp.message(Command("reminders"))
async def reminders(message: Message):

    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            """
            SELECT text
            FROM reminders
            WHERE user_id=?
            """,
            (message.from_user.id,)
        )
        rows = await cursor.fetchall()

    if not rows:
        await message.answer("Напоминаний нет")
        return

    text = "⏰ Напоминания:\n\n"

    for row in rows:
        text += f"• {row[0]}\n"

    await message.answer(text)


# =========================
# SMART CHAT (NO COMMAND)
# =========================
@dp.message()
async def chat_handler(message: Message):

    if not message.text:
        return

    if message.text.startswith("/"):
        return

    await message.answer("🤖 Думаю...")

    answer = ask_ai(message.from_user.id, message.text)

    await message.answer(answer)


# =========================
# MAIN
# =========================
async def main():

    await init_db()

    print("BOT STARTED")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
