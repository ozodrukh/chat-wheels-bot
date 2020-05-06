import flask
import os

from chat_wheel import ChatWheelStorage, VoiceEncoder
from gamepedia_wheel_grabber import grab_voice_lines
from voice_generator import make_ogg_file_path, generate_ogg_from_source
from flask import request

app = flask.Flask(__name__)
storage = ChatWheelStorage()


@app.route("/get_wheel_voice_line")
def get_ogg_voice():
    voice_id = request.args["id"]
    voice = storage.get_voice_object(voice_id)

    if voice is None:
        return flask.make_response(flask.jsonify(status="not_found"), 404)

    voice_file = make_ogg_file_path(voice_id, os.path.join(os.getcwd(), "voicelines", "files"))

    if not os.path.exists(voice_file):
        generate_ogg_from_source(voice.url, voice_file)

    return flask.send_file(voice_file,
                           mimetype="audio/ogg",
                           as_attachment=True)


@app.route("/search")
def search():
    return flask.json.dumps(storage.search(request.args["query"]), cls=VoiceEncoder, allow_nan=False)


@app.route("/update_voice_lines")
def update_voice_lines():
    if len(grab_voice_lines(storage)) > 0:
        return "ok"
    else:
        return "failed"

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=80)
