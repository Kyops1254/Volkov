import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from dotenv import load_dotenv

import aiosqlite

from database import init_db

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)

dp = Dispatcher()

DB = "study.db"


# START

@dp.message(Command("start"))
async def start(message: Message):

    await message.answer(
        "📚 Study Bot\n\n"
        "Команды:\n"
        "/add_homework\n"
        "/homework\n"
        "/add_grade\n"
        "/grades\n"
        "/add_reminder\n"
        "/reminders"
    )


# HOMEWORK

@dp.message(Command("add_homework"))
async def add_homework(message: Message):

    try:

        data = message.text.replace(
            "/add_homework ",
            ""
        )

        subject, task = data.split("|")

        async with aiosqlite.connect(DB) as db:

            await db.execute(
                """
                INSERT INTO homework
                (user_id,subject,task)
                VALUES(?,?,?)
                """,
                (
                    message.from_user.id,
                    subject.strip(),
                    task.strip()
                )
            )

            await db.commit()

        await message.answer("✅ Домашка добавлена")

    except:

        await message.answer(
            "Пример:\n"
            "/add_homework Math | page 10"
        )


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


# GRADES

@dp.message(Command("add_grade"))
async def add_grade(message: Message):

    try:

        args = message.text.split()

        subject = args[1]
        grade = args[2]

        async with aiosqlite.connect(DB) as db:

            await db.execute(
                """
                INSERT INTO grades
                (user_id,subject,grade)
                VALUES(?,?,?)
                """,
                (
                    message.from_user.id,
                    subject,
                    grade
                )
            )

            await db.commit()

        await message.answer("✅ Оценка добавлена")

    except:

        await message.answer(
            "Пример:\n"
            "/add_grade Math 5"
        )


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


# REMINDERS

@dp.message(Command("add_reminder"))
async def add_reminder(message: Message):

    text = message.text.replace(
        "/add_reminder ",
        ""
    )

    async with aiosqlite.connect(DB) as db:

        await db.execute(
            """
            INSERT INTO reminders
            (user_id,text)
            VALUES(?,?)
            """,
            (
                message.from_user.id,
                text
            )
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


# MAIN

async def main():

    await init_db()

    print("BOT STARTED")

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
