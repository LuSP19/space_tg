import os
from datetime import datetime
from pathlib import Path
from time import sleep
from urllib.parse import unquote, urlparse

import requests
import telegram
from dotenv import load_dotenv


def extract_ext(url):
    path = unquote(urlparse(url).path)
    return os.path.splitext(path)[1]


def get_image(directory, filename, image_link, params=None):
    file_path = Path(directory)/filename
    response = requests.get(image_link, params=params)
    response.raise_for_status()

    with file_path.open('wb') as file:
        file.write(response.content)


def fetch_spacex_launch_images(directory, launch_number):
    url = 'https://api.spacexdata.com/v4/launches/'
    response = requests.get(url)
    response.raise_for_status()
    space_x_resp = response.json()[launch_number]
    image_links = space_x_resp['links']['flickr']['original']
    
    for image_number, image_link in enumerate(image_links, start=1):
        filename = 'spacex{0}{1}'.format(image_number, extract_ext(image_link))
        get_image(directory, filename, image_link)


def fetch_nasa_images(directory, count, nasa_api_key):
    url = 'https://api.nasa.gov/planetary/apod'
    params = {'api_key':nasa_api_key, 'count':count}
    nasa_images = []
    response = requests.get(url, params=params)
    response.raise_for_status()

    for item in response.json():
        nasa_images.append(item['hdurl'])
    
    for image_number, image_link in enumerate(nasa_images, start=1):
        filename = 'nasa{0}{1}'.format(image_number, extract_ext(image_link))
        get_image(directory, filename, image_link)


def fetch_nasa_epic_images(directory, nasa_api_key):
    url = 'https://api.nasa.gov/EPIC/api/natural/images'
    img_url_template = 'https://api.nasa.gov/EPIC/archive/natural/{0}/png/{1}.png'
    params = {'api_key':nasa_api_key}
    response = requests.get(url, params=params)
    response.raise_for_status()

    for item in response.json():
        image_id = item['image']
        image_timestamp = image_id.split('_')[-1]
        image_datetime = datetime.strptime(f'{image_timestamp}', '%Y%m%d%H%M%S')
        image_timestamp_path = image_datetime.strftime('%Y/%m/%d')
        image_link = img_url_template.format(image_timestamp_path, image_id)
        filename = '{0}.png'.format(image_id)
        get_image(directory, filename, image_link, params=params)


def main():
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


if __name__ == '__main__':
    main()