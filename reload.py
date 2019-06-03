# 1. Toda vez que o computador iniciar:
# 2. Ir na api, baixar todos os json
# 3. baixar todas as imagens novas
# 4. colocar tudo isso em uma pasta
# 5. start no site no browser. (edited)
import requests
import json

url = 'http://small-big-api.herokuapp.com/photo/processed'


def get_json():
    response = requests.get(url, stream=False)
    result = response.json()

    with open('processed.json', 'w+') as file:
        result = json.dumps(result, indent=3)
        file.write(result)
    print("The processed.json was updated!")
    file.close()
