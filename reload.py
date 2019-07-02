import os
import json
import requests
from urllib.request import urlopen
import time
from datetime import datetime
from datetime import timedelta
from download_images import image_limiter

url = 'http://small-big-api.herokuapp.com/photo/processed'
url_location = 'http://127.0.0.1:5000/location'
url_hashtag = 'https://small-big-api.herokuapp.com/hashtag/'
time_url = 'http://just-the-time.appspot.com/'
time_update = 0


def get_json():
    # If someone remove this folder, the project will crash.
    if not os.path.exists('imgs'):
        os.mkdir('imgs')
    if not os.path.exists('imgs/small'):
        os.mkdir('imgs/small')

    # processed.json
    response = requests.get(url_location, stream=False)
    r = requests.get(url_hashtag, stream=False)
    print(response)
    print(r)
    if not response.ok or not r.ok:
        reload()
    else:
        result = response.json()
        hashtag_result = r.json()
        with open('location.json', 'w+') as file:
            result = json.dumps(result, indent=3)
            file.write(result)
            file.close()
        print("The location.json was updated!")

        with open('hashtags.json', 'w+') as file:
            result = json.dumps(hashtag_result, indent=3)
            file.write(result)
            file.close()
        print("The hashtags.json was updated!")

        print("Downloading images")
        image_limiter()
        print("Waiting to next update")
        reload()


def reload():
    # Check if the website is on
    if str(urlopen(time_url).getcode()) == '200':
        # UTC(0), BRT(-3)
        response = urlopen(time_url)
        date = (response.read().strip()).decode('utf-8') + '.0'
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        date = date - timedelta(hours=3)  # UTC - BRT
    else:
        date = datetime.now()

    print(date)
    if date.hour == time_update:
        print("Updating")
        get_json()

    time.sleep(60 * 15)
    reload()


print("Starting...")
get_json()
