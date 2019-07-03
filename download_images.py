import os
import dotenv
from math import ceil
import json
from PIL import Image
from io import BytesIO
import requests
import dropbox
from dropbox.files import WriteMode
import getpass
from idna import unicode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv.load_dotenv(os.path.join(BASE_DIR, '.env'))

size = 150, 150
url = 'http://small-big-api.herokuapp.com/photo'
path = f'C:/Users/{getpass.getuser()}/Documents/Hub9/auto_reload/dist/reload/imgs/small/'
dbx_path = '/nwjs-v0.38.4-win-x64/public/imgs/small/'
dbx = dropbox.Dropbox('9dXiur3lW-AAAAAAAAAAC2DXsDaGJgscGQbQpz1ZOvKAl8pGxNR4Al3CgeSp96LU')
url_postmon = 'http://api.postmon.com.br/v1/cep/'
limit = 500
#path = f'C:/Users/{getpass.getuser()}/Desktop/Hub9/auto_reload/imgs/small/'
#dbx_path = '/teste/imgs/small/'


def download_images():
    if not dbx.files_list_folder('').entries:
        dbx.files_create_folder('/nwjs-v0.38.4-win-x64/public/imgs/small')
        dbx.files_create_folder('/nwjs-v0.38.4-win-x64/public/assets/json')

    img_count, img_downloaded, img_response_failed = 0, 0, 0

    with open('processed.json', 'r') as file:
        result = json.loads(file.read())
        for small_big in result['result']:
            shortcode_jpg = small_big['shortcode'] + '.jpg'
            try:
                photo = dbx.files_alpha_get_metadata(f"{dbx_path}{shortcode_jpg}")
            except:
                photo = ''

            try:
                img_count += 1
                if not photo == shortcode_jpg:
                    img_downloaded += 1
                    print('------------------------------------------------')
                    response = requests.get(small_big['image_url'], stream=True)

                    if not response.ok:
                        img_response_failed += 1
                        delete = requests.delete(url + '/delete/' + small_big['shortcode'])
                        print(f"The shortcode {small_big['shortcode']} was deleted!")
                    else:
                        print(small_big['shortcode'])
                        img = Image.open(BytesIO(response.content)).convert('RGB')
                        img.thumbnail(size, Image.ANTIALIAS)
                        img.save(path + shortcode_jpg, "JPEG")
                        print(f"The {small_big['shortcode']} is uploading")
                        with open(path + shortcode_jpg, 'rb') as f:
                            try:
                                dbx.files_upload(f.read(), f"{dbx_path}{shortcode_jpg}",
                                mode=WriteMode('overwrite'))
                                print(path + shortcode_jpg)
                                f.close()
                                os.remove(path + shortcode_jpg)
                            except:
                                print("WARNING: uploud failed!")

                    img_percent = img_response_failed / img_downloaded
                    print(f'Downloaded images status:\n'
                          f'{"%.2f"%(img_percent)}% failed | '
                          f'{"%.2f"%(100 - img_percent)}% completed | '
                          f'images total: {img_downloaded}')
                else:
                    print('------------------------------------------------')
                    print(f"Image {small_big['shortcode']} already was added")

            except Exception as e:
                if os.path.exists(path + shortcode_jpg):
                    os.remove(path + shortcode_jpg)
                print('Unexpected error:' + str(e))

        file.close()

    print("The images were updated!")

    with open('percentual.json', 'rb') as f:
        try:
            dbx.files_upload(f.read(), f'/nwjs-v0.38.4-win-x64/public/assets/json/{f}',
                             mode=WriteMode('overwrite'))
        except:
            print("WARNING: percentual.json uploud failed!")
        f.close()

    with open('hashtags.json', 'rb') as f:
        try:
            dbx.files_upload(f.read(), f'/nwjs-v0.38.4-win-x64/public/assets/json/{f}',
                             mode=WriteMode('overwrite'))
        except:
            print("WARNING: hashtags.json uploud failed!")
        f.close()

    with open('processed.json', 'rb') as f:
        try:
            dbx.files_upload(f.read(), f'/nwjs-v0.38.4-win-x64/public/assets/json/{f}',
                             mode=WriteMode('overwrite'))
        except:
            print("WARNING: processed.json uploud failed!")
        f.close()


def image_limiter():
    with open('location.json', 'r') as file:
        result = json.loads(file.read())
        images_total = result[0]['Images total']
        images = []
        processed = {"pages": "?", "result": []}
        percentual = {}
        for zone in result[1:]:
            for z in zone:
                per = ((100 * zone[z][0]['count']) / images_total)
                percentual[z] = f"{'%.2f'%(per)}%"

                zone_limit = ceil(per * limit / 100)
                processed['result'].append(zone[z][1:zone_limit])
    processed['result'] = [j for i in processed['result'] for j in i]

    with open('percentual.json', 'w+', encoding='utf8') as file:
        result = json.dumps(percentual, indent=3, ensure_ascii=False)
        file.write(unicode(result))
        file.close()

    with open('processed.json', 'w+', encoding='utf8') as file:
        result = json.dumps(processed, indent=3)
        file.write(result)
        file.close()

    download_images()

image_limiter()
