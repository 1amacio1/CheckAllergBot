import pytesseract
from PIL import Image
from aiogram import Bot, Dispatcher, types
from aiogram.types import ContentType
from aiogram import executor
from config import TOKEN_API
import re

pytesseract.pytesseract.tesseract_cmd = r'C://Program Files//Tesseract-OCR//tesseract.exe'


# Инициализация бота и диспетчера
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

# Список аллергенов для поиска
ALLERGENS = [
    'молоко', 'яйцо', 'рыба', 'арахис', 'соя', 'пшеница', 
    'орехи', 'миндаль', 'грецкий орех', 'фундук', 'кешью',
    'горчица', 'кунжут', 'люпин', 'сернистый ангидрид', 'апельсиновый сок'
]

HELP_COMMAND = """
<b>Вот список доступных команд:</b>
📍 /start - начать работу бота
📍 /analyse - анализ состава
📍 /info - информация о боте
📍 /help - список команд
📍 /links - полезные ссылки
"""

START_COMMAND = """
Привет!👋
Я бот который поможет тебе проанализировать состав продукта и выявить возможные аллергены

Нажми /help, чтобы увидеть список команд
"""

INFO_COMMAND = """
<b>Этот бот поможет тебе обнаружить в составе продукта потенциальные аллергены!🥥
Необходимо лишь скинуть в чат фотографию состава и бот незамедлительно выявит продукты

Нажми /help, чтобы увидеть список команд!</b>
"""

HELPFUL_LINKS = """
<b>Здесь есть интересные и полезные ссылки:</b>
📍 https://www.kp.ru/family/eda/produkty-allergeny/ - пищевые аллергены
📍 https://suprastin.net/encyclopedia/allergeny/ - "энциклопедия" для аллергиков
📍 https://wer.ru/articles/top-preparatov-ot-allergii-antigistaminnye/ - антигистоминные препараты
"""

async def on_startup(dp):
    await bot.set_my_commands([
        types.BotCommand('start', 'начать работу с ботом'),
        types.BotCommand('help', 'доступные команды'),
        types.BotCommand('analyse', 'анализ состава'),
        types.BotCommand('info', 'информация о боте'),
        types.BotCommand('links', 'полезные ссылки')
    ])

# Функция для распознавания текста и поиска аллергенов
def find_allergens(image_path):
    # Распознаем текст на изображении
    text = pytesseract.image_to_string(Image.open(image_path), lang='rus')
    found_allergens = []
    # Поиск аллергенов в тексте
    for allergen in ALLERGENS:
        if re.search(rf'\b{allergen}\b', text, re.IGNORECASE):
            found_allergens.append(allergen)
    return found_allergens, text

# Обработчик для сообщений с фотографиями
@dp.message_handler(content_types=ContentType.PHOTO)
async def handle_photo(message: types.Message):
    # Скачиваем фотографию
    photo = message.photo[-1]  # Берем изображение в самом высоком разрешении
    file_path = await photo.download(destination_file='photo.png')

    # Ищем аллергены на фото
    allergens, recognized_text = find_allergens('photo.png')

    if allergens:
        allergen_list = ', '.join(allergens)
        await message.reply(f"Обнаружены возможные аллергены: {allergen_list}\n\nНажмите /help, чтобы выйти в меню!")
    else:
        await message.reply("Аллергены не обнаружены.\n\nНажмите /help, чтобы выйти в меню!")
    
    # Для справки: отправляем распознанный текст
    # await message.reply(f"Распознанный текст:\n{recognized_text}")

@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    await bot.send_message(text=START_COMMAND, chat_id=message.from_user.id, parse_mode="HTML")

# Обработчик для текстовых сообщений
@dp.message_handler(commands=["help"])
async def help_user(message: types.Message):
    await bot.send_message(text=HELP_COMMAND, chat_id=message.from_user.id, parse_mode="HTML")

@dp.message_handler(commands=["info"])
async def inf_command(message: types.Message):
    await bot.send_message(text=INFO_COMMAND, chat_id=message.from_user.id, parse_mode="HTML")

@dp.message_handler(commands=["analyse"])
async def analyse_photo(message: types.Message):
    await bot.send_message(text="Пришли мне фотографию состава и я найду продукты, которые потенциально могут вызвать аллергию..", chat_id=message.from_user.id)
    
@dp.message_handler(commands=["links"])
async def links_command(message: types.Message):
    await bot.send_message(text=HELPFUL_LINKS, chat_id=message.from_user.id, disable_web_page_preview=True, parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)