import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = "ТУТ_ТВОЙ_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ---------------- DATABASE ----------------

async def init_db():
    async with aiosqlite.connect("notes.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT
            )
        """)
        await db.commit()


# ---------------- COMMANDS ----------------

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "Привет! Я учебный бот 📚\n\n"
        "Команды:\n"
        "/add <текст> — добавить заметку\n"
        "/notes — показать заметки\n"
        "/delete <id> — удалить заметку\n"
        "/help — помощь"
    )


@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "/add <текст>\n/notes\n/delete <id>"
    )


@dp.message(Command("add"))
async def add_note(message: Message):
    text = message.text.replace("/add", "").strip()

    if not text:
        await message.answer("Напиши текст заметки после команды")
        return

    async with aiosqlite.connect("notes.db") as db:
        await db.execute(
            "INSERT INTO notes (user_id, text) VALUES (?, ?)",
            (message.from_user.id, text)
        )
        await db.commit()

    await message.answer("Заметка добавлена ✅")


# ---------------- MAIN ----------------

async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
