import os
import time
import json
import requests


def download_images():
    img_count, img_reponse_failed = 0, 0

    with open('processed.json', 'r') as file:
        result = json.loads(file.read())
        for small_big in result['result']:
            path = 'imgs/'+small_big['shortcode'] + '.jpg'
            try:
                if not os.path.exists(path):
                    with open(path, 'wb') as handle:
                        img_count += 1
                        print(small_big['shortcode'])
                        response = requests.get(small_big['image_url'], stream=True)
                        if not response.ok:
                            print(response)
                            img_reponse_failed += 1
                            delete = requests.delete(path + '/delete/' + small_big['shortcode'])
                        for block in response.iter_content(1024):
                            if not block:
                                break
                            handle.write(block)

                    img_percent = img_reponse_failed / img_count
                    print(f'Downloaded images status:\n'
                          f'{"%.2f"%(img_percent)}% failed | '
                          f'{"%.2f"%(100 - img_percent)}% completed | '
                          f'images total: {img_count}')
                else:
                    print(f"Image {path} already was added")
            except:
                os.remove(path)

download_images()
