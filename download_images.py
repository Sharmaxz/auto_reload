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
path = f'C:/Users/{getpass.getuser()}/Documents/Hub9/auto_reload/imgs/small/'
dbx_path = '/nwjs-v0.38.4-win-x64/public/imgs/small/'
dbx = dropbox.Dropbox('9dXiur3lW-AAAAAAAAAAC2DXsDaGJgscGQbQpz1ZOvKAl8pGxNR4Al3CgeSp96LU') #os.environ.get('DROPBOX_TOKEN', ''))


def download_images():
    if not dbx.files_list_folder('').entries:
        dbx.files_create_folder('/nwjs-v0.38.4-win-x64/public/imgs/small')
        dbx.files_create_folder('/nwjs-v0.38.4-win-x64/public/assets/json')

    img_count, img_reponse_failed = 0, 0

    with open('processed.json', 'r') as file:
        result = json.loads(file.read())
        for small_big in result['result']:

            shortcode_jpg = small_big['shortcode'] + '.jpg'
            try:
                photo = dbx.files_alpha_get_metadata(f"{dbx_path}{shortcode_jpg}")
            except:
                photo = ''
            print(photo)

            try:
                if not photo == shortcode_jpg:
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
                        img.thumbnail(size, Image.ANTIALIAS)
                        img.save(path + shortcode_jpg, "JPEG")
                        print(f"The {small_big['shortcode']} is uploading")
                        with open(path + shortcode_jpg + '.jpg', 'rb') as f:
                            try:
                                dbx.files_upload(f.read(), f"{dbx_path}{shortcode_jpg}",
                                mode=WriteMode('overwrite'))
                                os.remove(path + shortcode_jpg)
                            except:
                                print("WARNING: uploud failed!")

                    img_percent = img_reponse_failed / img_count
                    print(f'Downloaded images status:\n'
                          f'{"%.2f"%(img_percent)}% failed | '
                          f'{"%.2f"%(100 - img_percent)}% completed | '
                          f'images total: {img_count}')
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
            print("WARNING: uploud failed!")

# download_images()
