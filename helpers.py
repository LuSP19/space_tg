import os
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests


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

    for image_number, item in enumerate(response.json(), start=1):
        filename = 'nasa{0}{1}'.format(image_number, extract_ext(item['hdurl']))
        get_image(directory, filename, item['hdurl'])


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
