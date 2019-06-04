import os
import json
import requests
from download_images import download_images

url = 'http://small-big-api.herokuapp.com/photo/processed'


def get_json():
    # If someone remove this folder, the project will crash.
    os.mkdir('imgs')
    response = requests.get(url, stream=False)
    result = response.json()

    with open('processed.json', 'w+') as file:
        result = json.dumps(result, indent=3)
        file.write(result)
        file.close()
    print("The processed.json was updated!")
    download_images()


def reload():
    # TODO: to write the code that's responsible to time of updated
    get_json()
