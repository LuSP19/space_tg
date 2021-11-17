import os
from pathlib import Path
from time import sleep

import telegram
from dotenv import load_dotenv

from helpers import fetch_spacex_launch_images, fetch_nasa_images, \
    fetch_nasa_epic_images


load_dotenv()
nasa_api_key = os.getenv('NASA_API_KEY')
tg_bot_token = os.getenv('TG_BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')
delay = int(os.getenv('SPACE_IMAGES_SEND_DELAY', '86400'))
directory = 'images'
nasa_images_count = 10
spacex_launch_number = 12

Path(directory).mkdir(parents=False, exist_ok=True)

fetch_spacex_launch_images(directory, spacex_launch_number)
fetch_nasa_images(directory, nasa_images_count, nasa_api_key)
fetch_nasa_epic_images(directory, nasa_api_key)

bot = telegram.Bot(token=tg_bot_token)
space_images = os.listdir(directory)

while space_images:
    file_path = os.path.join(directory, space_images.pop())
    with open(file_path, 'rb') as photo:
        bot.send_photo(chat_id=chat_id, photo=photo)
    sleep(delay)

print('All images have been sent')
