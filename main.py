import os
from pathlib import Path
from time import sleep
from urllib.parse import unquote, urlparse

import requests
import telegram
from dotenv import load_dotenv


def extract_ext(url):
    path = unquote(urlparse(url).path)
    filename = os.path.split(path)[1]
    return os.path.splitext(filename)[1]


def fetch_spacex_last_launch(directory):
    url = 'https://api.spacexdata.com/v4/launches/'
    response = requests.get(url)
    space_x_resp = response.json()[12]
    image_links = space_x_resp['links']['flickr']['original']
    
    for image_number, image_link in enumerate(image_links, start=1):
        filename = 'spacex{0}{1}'.format(str(image_number), extract_ext(image_link))
        file_path = Path(directory)/filename
        response = requests.get(image_link)
        response.raise_for_status
    
        with file_path.open('wb') as file:
            file.write(response.content)


def fetch_nasa_images(directory, count, nasa_api_key):
    url = 'https://api.nasa.gov/planetary/apod'
    params = {'api_key':nasa_api_key, 'count':count}
    nasa_images = []
    response = requests.get(url, params=params)

    for item in response.json():
        nasa_images.append(item['hdurl'])
    
    for image_number, image_link in enumerate(nasa_images, start=1):
        filename = 'nasa{0}{1}'.format(str(image_number), extract_ext(image_link))
        file_path = Path(directory)/filename
        response = requests.get(image_link)
        response.raise_for_status
    
        with file_path.open('wb') as file:
            file.write(response.content)


def fetch_nasa_epic_images(directory, nasa_api_key):
    url = 'https://api.nasa.gov/EPIC/api/natural/images'
    img_url_template = 'https://api.nasa.gov/EPIC/archive/natural/{0}/{1}/{2}/png/{3}.png'
    params = {'api_key':nasa_api_key}
    response = requests.get(url, params=params)

    for item in response.json():
        image_id = item['image']
        year_month_day = item['image'].split('_')[2][:8]
        year = year_month_day[:4]
        month = year_month_day[4:6]
        day = year_month_day[6:]

        image_url = img_url_template.format(year, month, day, image_id)
        filename = '{0}.png'.format(image_id)
        file_path = Path(directory)/filename
        response = requests.get(image_url, params=params)
        response.raise_for_status

        with file_path.open('wb') as file:
            file.write(response.content)


def main():
    load_dotenv()
    nasa_api_key = os.getenv('NASA_API_KEY')
    tg_bot_token = os.getenv('TG_BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    delay = os.getenv('SPACE_IMAGES_SEND_DELAY')
    if delay:
        delay = int(delay)
    else:
        delay = 86400
    directory = 'images'
    nasa_images_count = 10

    Path(directory).mkdir(parents=False, exist_ok=True)

    fetch_spacex_last_launch(directory)
    fetch_nasa_images(directory, nasa_images_count, nasa_api_key)
    fetch_nasa_epic_images(directory, nasa_api_key)

    bot = telegram.Bot(token=tg_bot_token)
    space_images = os.listdir(directory)

    while True:
        if space_images:
            file_path = os.path.join(directory, space_images.pop())
            bot.send_photo(chat_id=chat_id, photo=open(file_path, 'rb'))
            sleep(delay)
        else:
            print('All images have been sent')
            break


if __name__ == '__main__':
    main()