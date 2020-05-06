import bs4
import requests
import json

from chat_wheel import Voice, ChatWheelStorage, VoiceEncoder


def grab_voice_lines(storage: ChatWheelStorage):
    storage.clear()

    voice_lines = []

    response = requests.get("https://dota2.gamepedia.com/Chat_Wheel")
    parser = bs4.BeautifulSoup(response.content, "html.parser")
    available_audio = parser.select(".wikitable audio")

    for audio in available_audio:
        audio_block = audio.parent.parent
        audio_name = audio_block.contents[-1]

        voice = Voice()
        voice.name = get_name(audio_name)
        voice.url = audio.select_one("source")["src"]

        storage.save_voice_object(voice)
        voice_lines.append(voice)

    print(json.dumps(storage.search("lakad"), cls=VoiceEncoder))

    chatwheels_json = open("voicelines/dota2_chat_wheels.json", "w+")
    chatwheels_json.write(json.dumps(voice_lines, cls=VoiceEncoder))
    return voice_lines


def get_name(audio_name):
    name: str = None
    if type(audio_name) is bs4.NavigableString:
        name = audio_name
    elif type(audio_name) is bs4.Tag:
        if audio_name.name == "span":
            name = audio_name.text + " [" + audio_name["title"] + "]"
        else:
            name = audio_name.text

    if name is not None:
        name = name.strip()
    return name


if __name__ == "__main__":
    grab_voice_lines()
