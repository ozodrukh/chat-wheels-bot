import voice_generator
import json, os
import dataset
import sqlite3

if __name__ == "__main__":
    dota2_wheel_file = open("voicelines/dota2_chat_wheels.json", "r")
    voice_lines: dict = json.loads("".join(dota2_wheel_file.readlines()))
    voice_line_names = list(voice_lines.keys())

    db = dataset.connect('sqlite:///factbook.db')
    table = db["users"]
    table.insert(dict(name="lol"))

    voice_line_id = 21
    voice_line_name = voice_line_names[voice_line_id]
    voice_line_url = voice_lines[voice_line_name]

    print(voice_line_name)

    file = voice_generator.make_ogg_file_path(voice_line_name,
                                              os.path.join(os.getcwd(), "voicelines", "files"))

    if not os.path.exists(file):
        voice_generator.generate_ogg_from_source(voice_line_url, file)
