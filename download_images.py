import os
import time
import json
from PIL import Image
from io import BytesIO
import requests

size = 150, 150
url = 'http://small-big-api.herokuapp.com/photo'

def download_images():
    img_count, img_reponse_failed = 0, 0
    with open('processed.json', 'r') as file:
        result = json.loads(file.read())
        for small_big in result['result']:
            # time.sleep(3)
            path_big = 'imgs/big/'+small_big['shortcode'] + '.jpg'
            path_small = 'imgs/small/'+small_big['shortcode'] + '.jpg'
            try:
                if not os.path.exists(path_big):
                    img_count += 1
                    print('------------------------------------------------')
                    response = requests.get(small_big['image_url'], stream=True)
                    if not response.ok:
                        img_reponse_failed += 1
                        delete = requests.delete(url + '/delete/' + small_big['shortcode'])
                        print(f"The shortcode {small_big['shortcode']} was deleted!")
                    else:
                        print(small_big['shortcode'])
                        img = Image.open(BytesIO(response.content)).convert('RGB')
                        big_image = img
                        big_image.save(path_big, "JPEG")
                        img.thumbnail(size, Image.ANTIALIAS)
                        img.save(path_small, "JPEG")

                    img_percent = img_reponse_failed / img_count
                    print(f'Downloaded images status:\n'
                          f'{"%.2f"%(img_percent)}% failed | '
                          f'{"%.2f"%(100 - img_percent)}% completed | '
                          f'images total: {img_count}')
                else:
                    print('------------------------------------------------')
                    print(f"Image {small_big['shortcode']} already was added")
            except Exception as e:
                if os.path.exists(path_small):
                    os.remove(path_small)
                if os.path.exists(path_big):
                    os.remove(path_big)
                print('Unexpected error:' + str(e))


    print("The images was updated!")


# download_images()
