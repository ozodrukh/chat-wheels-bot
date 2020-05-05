import flask
import os
from gamepedia_wheel_grabber import grab_voice_lines
from voice_generator import make_ogg_file_path, generate_ogg_from_source
from flask import request

app = flask.Flask(__name__)


@app.route("/get_wheel_voice_line")
def get_ogg_voice():
    url = request.args["url"]
    filename = request.args["filename"]

    voice_file = make_ogg_file_path(filename, os.path.join(os.getcwd(), "voicelines", "files"))

    if not os.path.exists(voice_file):
        generate_ogg_from_source(url, voice_file)

    return flask.send_file(voice_file,
                           mimetype="audio/ogg",
                           as_attachment=True)


@app.route("/update_voice_lines")
def update_voice_lines():
    if len(grab_voice_lines()) > 0:
        return "ok"
    else:
        return "failed"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)