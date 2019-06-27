import os
import dotenv
import time
import json
from PIL import Image
from io import BytesIO
import requests
import dropbox
from dropbox.files import WriteMode
import getpass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv.load_dotenv(os.path.join(BASE_DIR, '.env'))

size = 150, 150
url = 'http://small-big-api.herokuapp.com/photo'
path = f'C:/Users/{getpass.getuser()}/Documents/Hub9/auto_reload/dist/reload/imgs/small/'
dbx_path = '/nwjs-v0.38.4-win-x64/public/imgs/small/'
dbx = dropbox.Dropbox('9dXiur3lW-AAAAAAAAAAC2DXsDaGJgscGQbQpz1ZOvKAl8pGxNR4Al3CgeSp96LU')
url_postmon = 'http://api.postmon.com.br/v1/cep/'
limit = 30000
# path = f'C:/Users/{getpass.getuser()}/Desktop/Hub9/auto_reload/imgs/small/'
# dbx_path = '/teste/imgs/small/'


def average():
    location = {'no_zip_code': []}
    with open('processed.json', 'r') as file:
        result = json.loads(file.read())
        query_total = len(result['result'])

        for small_big in result['result']:
            try:
                address = json.loads(small_big['location']['address_json'])

                if address['zip_code']:
                    if '-' not in address['zip_code']:
                        address['zip_code'] = f"{address['zip_code'][:5]}-{address['zip_code'][5:9]}"

                    response = requests.get(url_postmon + address['zip_code'], stream=False)
                    r = response.json()

                    if r['bairro'] in location:
                        location[f"{r['bairro']}"].append(small_big['shortcode'])
                    else:
                        location[f"{r['bairro']}"] = [small_big['shortcode']]
                else:
                    location["no_zip_code"].append(small_big['shortcode'])

                # percent = sum(list(map(lambda l: len(location[l]), location)))
                # for key in location:
                #     percent_unit = (100 * len(location[key]))/percent
                #     percent_total = (100 * len(location[key]))/total
                #     print(f'{key}: {"%.2f"%(percent_unit)}% percent total: {"%.3f"%(percent_total)}%')
                # print(f'Total completed: {"%.3f"%(100 * percent/total)}%')

            except:
                print('Image does not have address_json!')
        location_total = sum(list(map(lambda l: len(location[l]), location)))
        average = location_total/query_total
        result = {}

        print('done!')

average()


def download_images():
    if not dbx.files_list_folder('').entries:
        dbx.files_create_folder('/nwjs-v0.38.4-win-x64/public/imgs/small')
        dbx.files_create_folder('/nwjs-v0.38.4-win-x64/public/assets/json')

    img_count, img_downloaded, img_response_failed = 0, 0, 0

    with open('processed.json', 'r') as file:
        result = json.loads(file.read())
        for small_big in result['result']:
            if img_count >= limit:
                break
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

    print("The images was updated!")

    with open('processed.json', 'rb') as f:
        try:
            dbx.files_upload(f.read(), f'/nwjs-v0.38.4-win-x64/public/assets/json/{f}',
                             mode=WriteMode('overwrite'))
        except:
            print("WARNING: processed.json uploud failed!")

    with open('hashtags.json', 'rb') as f:
        try:
            dbx.files_upload(f.read(), f'/nwjs-v0.38.4-win-x64/public/assets/json/{f}',
                             mode=WriteMode('overwrite'))
        except:
            print("WARNING: hashtags.json uploud failed!")


# download_images()
