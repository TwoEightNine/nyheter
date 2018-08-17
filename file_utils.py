from base64 import b64decode
import os

PHOTOS_DIR = os.path.join(os.path.dirname(__file__), 'photos/')

STUB_PATH = '000000.jpg'


def init_before():
    try:
        os.mkdir(PHOTOS_DIR)
    except FileExistsError:
        pass


def save_photo(avatar, id):
    try:
        avatar = b64decode(avatar)
    except TypeError:
        return False
    jpg = is_jpg(avatar)
    png = is_png(avatar)
    if not jpg and not png:
        return False
    ext = '.jpg' if jpg else '.png'
    with open(get_avatar_path(id, ext=ext), 'wb') as f:
        f.write(avatar)
    return True


def get_avatar_path(id, stub=False, ext='.jpg'):
    path = PHOTOS_DIR + str(id).zfill(6) + ext
    if not stub:
        return path
    else:
        if os.path.isfile(path):
            return path
        else:
            return PHOTOS_DIR + STUB_PATH


def get_last_id():
    only_files = [f for f in os.listdir(PHOTOS_DIR) if os.path.isfile(os.path.join(PHOTOS_DIR, f))]
    only_files.sort()
    if len(only_files) == 0:
        return 0
    last = only_files[-1].split('.')[0]
    return int(last)


def get_photo_url(photo_id=0):
    only_files = [f for f in os.listdir(PHOTOS_DIR) if os.path.isfile(os.path.join(PHOTOS_DIR, f))]
    for file in only_files:
        if file.startswith(str(photo_id).zfill(6)):
            return PHOTOS_DIR + file
    return PHOTOS_DIR + STUB_PATH


def is_png(raw):
    return raw[:8] == b'\x89PNG\r\n\x1a\n'


def is_jpg(raw):
    return raw[:3] == b'\xff\xd8\xff'
