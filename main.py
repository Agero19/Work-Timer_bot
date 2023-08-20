import json
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

bot_token = config.get('bot_token')

# Initialize your bot with the token
bot = Bot(token=bot_token)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

try:
    with open('work_records.json', 'r') as f:
        work_records = json.load(f)
except FileNotFoundError:
    work_records = {}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [types.KeyboardButton(text="Start working"), types.KeyboardButton(text="Finish work"),
               types.KeyboardButton(text="My Records")]
    keyboard.add(*buttons)

    await message.reply(
        "Welcome to Work-Timer-Bot! This bot helps you keep track of your work hours.\n"
        "Please choose an option:",
        reply_markup=keyboard
    )


@dp.message_handler(lambda message: message.text == "Start working")
async def start_working(message: types.Message):
    chat_id = message.chat.id
    current_time = datetime.datetime.now().strftime("%H:%M-%d/%m/%Y")
    if chat_id not in work_records:
        work_records[chat_id] = []
    work_records[chat_id].append({'start_time': current_time})
    await message.reply(f"You started working at {current_time}")


@dp.message_handler(lambda message: message.text == "Finish work")
async def finish_working(message: types.Message):
    chat_id = message.chat.id
    current_time = datetime.datetime.now().strftime("%H:%M-%d/%m/%Y")
    if chat_id in work_records and work_records[chat_id][-1].get('end_time') is None:
        work_records[chat_id][-1]['end_time'] = current_time
        start_time = datetime.datetime.strptime(
            work_records[chat_id][-1]['start_time'], "%H:%M-%d/%m/%Y")
        end_time = datetime.datetime.strptime(
            work_records[chat_id][-1]['end_time'], "%H:%M-%d/%m/%Y")
        total_work_time = end_time - start_time
        work_records[chat_id][-1]['total_work_time'] = str(total_work_time)
        await message.reply(f"You finished your work at {current_time}. "
                            f"Total time of work: {total_work_time}.")
    else:
        await message.reply("You haven't started working yet or you've already finished your work.")


@dp.message_handler(lambda message: message.text == "My Records")
async def get_records(message: types.Message):
    chat_id = message.chat.id
    if chat_id in work_records:
        records = work_records[chat_id]
        record_text = "\n".join(
            f"{index + 1}) {record['start_time'].split('-')[1]} - from {record['start_time'].split('-')[0]} to {record['end_time'].split('-')[0]}"
            for index, record in enumerate(records)
        )
        await message.reply(record_text, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply("No work records available.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
