import os
from functools import partial
from subprocess import Popen, PIPE

from flask import Flask, Response  # $ pip install flask

mp3file = 'static/5566.mp3'
app = Flask(__name__)


@app.route('/')
def index():
    return """<!doctype html>
<title>Play {mp3file}</title>
<audio controls autoplay >
    <source src="{mp3file}" type="audio/mp3" >
    Your browser does not support this audio format.
</audio>""".format(mp3file=mp3file)


@app.route('/' + mp3file)
def stream():
    process = Popen(['cat', mp3file], stdout=PIPE, bufsize=-1)
    read_chunk = partial(os.read, process.stdout.fileno(), 1024)
    return Response(iter(read_chunk, b''), mimetype='audio/mp3')

if __name__ == "__main__":
    app.run(host = os.getenv('IP', "0.0.0.0"), port = int(os.getenv('PORT', 8000)), threaded = True)