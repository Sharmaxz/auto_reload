import os
import time
import json
from PIL import Image
from io import BytesIO
import requests

size = 150, 150


def download_images():
    img_count, img_reponse_failed = 0, 0
    with open('processed.json', 'r') as file:
        result = json.loads(file.read())
        for small_big in result['result']:
            time.sleep(3)
            path = 'imgs/big/'+small_big['shortcode'] + '.jpg'
            try:
                if not os.path.exists(path):
                    with open(path, 'wb') as handle:
                        img_count += 1
                        print('-------------------------------------------------')
                        response = requests.get(small_big['image_url'], stream=True)
                        if not response.ok:
                            img_reponse_failed += 1
                            print(f"The shortcode {small_big['shortcode']} was deleted!")
                            delete = requests.delete(path + '/delete/' + small_big['shortcode'])
                        else:
                            print(small_big['shortcode'])
                            img = Image.open(BytesIO(response.content)).convert('RGB')
                            big_image = img
                            big_image.save('imgs/big/' + small_big['shortcode'] + '.jpg', "JPEG")
                            img.thumbnail(size, Image.ANTIALIAS)
                            img.save('imgs/small/' + small_big['shortcode'] + '.jpg', "JPEG")

                    img_percent = img_reponse_failed / img_count
                    print(f'Downloaded images status:\n'
                          f'{"%.2f"%(img_percent)}% failed | '
                          f'{"%.2f"%(100 - img_percent)}% completed | '
                          f'images total: {img_count}')
                else:
                    print('-------------------------------------------------')
                    print(f"Image {path} already was added")
            except:
                os.remove(path)

    print("The images was updated!")


# download_images()
