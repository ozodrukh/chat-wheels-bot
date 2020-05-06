import os

import requests


def generate_ogg_from_source(url: str, filename: str):
    r = requests.get(url, stream=True)
    tmp_file = filename + ".tmp"

    with open(tmp_file, "wb") as fd:
        for chunk in r.iter_content(128):
            fd.write(chunk)

    print("ffmpeg -i {} -c:a libopus -b:a 128k {}".format(tmp_file, filename))
    print(os.popen("ffmpeg -i {} -c:a libopus -b:a 128k {}".format(tmp_file, filename)).read())
    #
    os.remove(tmp_file)


def make_ogg_file_path(filename: str, dir: str) -> str:
    return os.path.join(dir, (filename + ".ogg").replace(" ", "_"))