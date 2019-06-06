import os
import json
import requests
from urllib.request import urlopen
import time
from datetime import datetime
from datetime import timedelta
from download_images import download_images

url = 'http://small-big-api.herokuapp.com/photo/processed'
time_url = 'http://just-the-time.appspot.com/'
time_update = 0

def get_json():
    # If someone remove this folder, the project will crash.
    if not os.path.exists('imgs'):
        os.mkdir('imgs')
    response = requests.get(url, stream=False)
    print(response)
    result = response.json()

    with open('processed.json', 'w+') as file:
        result = json.dumps(result, indent=3)
        file.write(result)
        file.close()
    print("The processed.json was updated!")
    download_images()


def reload():

    # if date.hour == time_update:
    #     get_json

    #Check if the website is on
    if str(urlopen(time_url).getcode()) == '201':
        # UTC(0), BRT(-3)
        response = urlopen(time_url)
        date = (response.read().strip()).decode('utf-8') + '.0'
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        time = date.date() - timedelta(hours=3) # UTC - BRT
    else:
        date = datetime.now()


reload();
