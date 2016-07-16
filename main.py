# coding=utf-8
from flask import Flask, render_template, request, send_file, redirect, Response, send_from_directory, make_response, stream_with_context, url_for
import os
# from OpenSSL import SSL
import cv2, re, json, random, subprocess
from jinja2 import Environment, FileSystemLoader
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter
from functools import partial
from datetime import datetime
import sqlite3
app = Flask(__name__, static_url_path = "", static_folder = "static/")
app.debug = True
app.config['VIDEO_FOLDER'] = "media/video/"
app.config['ALLOWED_EXTENSIONS'] = set([
    # "txt",
    # "pdf",
    # "png", "jpg", "jpeg", "gif",
    "mp3",
    "mp4", "webm"
])
app.config['NGINX_PORT'] = 8000

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv

@app.route('/video/')
def randomVideo():
    with open('static/playlist.json', "r", encoding = 'utf8') as jsonFile:
        jsonData = json.load(jsonFile)
    return video(random.randrange(len(jsonData)))

@app.route('/video', defaults = {'videoNum':1})
@app.route('/video/<int:videoNum>')
def video(videoNum):
    return render_template('video.htm', videoNum = videoNum)

@app.route('/')
def index():
    return listRoot()

@app.route('/list/')
def listRoot():
    return list("")
@app.route('/list/<string:path>')
def list(path):
    def formattime(time):
        return datetime.strftime(
            datetime.fromtimestamp(time),
            '%Y-%m-%d %H:%M:%S'
        )
    files = []
    folderpath = os.path.join(app.config['VIDEO_FOLDER'] , path)
    for index, file in enumerate(os.listdir(folderpath)):
        filepath = os.path.join(folderpath, file)
        files.append({
            "index": index,
            "name": file,
            "url": ("/view/" if (os.path.isfile(filepath)) else "/list/") + file,
            "type": "file" if os.path.isfile(filepath) else "folder" if os.path.isdir(filepath) else "unknown",
            "mtime": formattime(os.path.getmtime(filepath)),
            "ctime": formattime(os.path.getctime(filepath)),
            "atime": formattime(os.path.getatime(filepath)),
            "size": os.path.getsize(filepath)
        })
    return render_template("list.htm", title = 'List', files = files, folderpath = path)
# def mimetype(filepath):
#     return magic.from_file(filepath)

@app.route('/view/<path:path>') # 強制檢視影片，而不是看瀏覽器而下載或觀看
def view(path):
    absolutePath = re.match(r"^http(s|)://[^/:]{1,}", request.url).group(0)
    return render_template('viewVideo.htm', videoFile = absolutePath + ":" + str(app.config['NGINX_PORT']) + "/" + path)

@app.route('/download/<path:path>') # 下載檔案(not work)
def download(path):
    # response = make_response()
    # response.headers["Content-Disposition"] = "attachment; filename=" + path
    return send_from_directory(app.config['VIDEO_FOLDER'], path, as_attachment = True)

@app.route('/youtube/<videoId>') # Youtube
def youtube(videoId):
    return render_template('iframe.htm', url = "https://www.youtube.com/embed/" + videoId + "?controls=1&disablekb=1&enablejsapi=1&autohide=1&modestbranding=1&playsinline=1&rel=0&showinfo=0&theme=dark&iv_load_poliucy=3&autoplay=1")

@app.route("/media/<path:path>") # 轉址到nginx伺服器
def media(path):
    mediaFileUrl = re.sub(r"(:[0-9]{0,}|)/media/", ":" + str(app.config['NGINX_PORT']) + "/", request.url) # nginx port
    # print("重導向: " + mediaFileUrl)
    return redirect(mediaFileUrl, code = 302)

@app.route('/stream/<script>') # PHP
def execute_python(script):
    return execute(script, "py")
@app.route('/stream/<script>.<scriptType>') # 執行Python檔案，即時回傳結果
def execute(script, scriptType):
    args = request.query_string.decode("utf-8").split("&")
    def inner():
        if (scriptType == "py"):
            cmd = ["python", "-u"]  # -u: don't buffer output
        elif (scriptType == "php"):
            cmd = ["php"]
        assert re.match(r'^[a-zA-Z._-]+$', script)
        exec_path = "script/" + script + "." + scriptType
        cmd.append(exec_path)
        cmd = cmd + args
        error = False
        proc = subprocess.Popen(
            cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
        )

        for line in proc.stdout:
            yield "<pre>" + line.decode("utf-8") + "</pre>"
            # yield highlight(line, BashLexer(), HtmlFormatter())

        # Maybe there is more stdout after an error...
        for line in proc.stderr:
            error = True
            yield highlight(line, BashLexer(), HtmlFormatter())

        if error:
            yield "<script>parent.stream_error()</script>"
        else:
            yield "<script>parent.stream_success()</script>"

    env = Environment(loader = FileSystemLoader('templates'))
    tmpl = env.get_template('stream.htm')
    return Response(tmpl.generate(result = inner()))

@app.route('/login/', methods = ['GET','POST'])
def login():
    if (request.method == 'POST'):
        return request.query_string.decode("utf-8")
    return render_template('login.htm', title = 'Login')

@app.route('/upload/', methods = ['GET','POST']) # 上傳檔案
def upload_file():
    if (request.method == 'POST'):
        files = request.files.getlist('files[]')
        uploadFilesStatus = []
        for file in files:
            filename = file.filename
            if allowed_file(filename):
                print("Uploaded a File!!")
                filename = filename_filter(filename)
                file.save(os.path.join(app.config['VIDEO_FOLDER'], filename))
                uploadFilesStatus.append((0, filename)) # 0: success
            else:
                print("Unsupported File Type!!")
                uploadFilesStatus.append((1, "Unsupported File Type")) # 1: failed
        successFiles = [info for status, info  in uploadFilesStatus if status == 0]
        return "<h2>上傳" + str(len(files)) + "個檔案中，成功" + str(len(successFiles)) + "個檔案</h2><p>" + "</p><p>".join(successFiles) + "</p>"
    return render_template('upload.htm', title = 'Upload')
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1] in app.config['ALLOWED_EXTENSIONS']
def filename_filter(filename):
    # filename = re.sub('[" "\/\--]+', '-', filename)
    # filename = re.sub(r':-', ':', filename)
    # filename = re.sub(r'^-|-$', '', filename)
    return filename

# @app.route('/camera/')
# def camera():
#     return Response(gen(Camera()), mimetype = "multipart/x-mixed-replace; boundary=frame")
# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield(b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


# class Camera(object):
#     def __init__(self):
#         # Using OpenCV to capture from device 0. If you have trouble capturing
#         # from a webcam, comment the line below out and use a video file
#         # instead.
#         self.video = cv2.VideoCapture(0)
#         # If you decide to use video.mp4, you must have this file in the folder
#         # as the main.py.
#         # self.video = cv2.VideoCapture('video.mp4')

#     def __del__(self):
#         self.video.release()

#     def get_frame(self):
#         success, image = self.video.read()
#         # We are using Motion JPEG, but OpenCV defaults to capture raw images,
#         # so we must encode it into JPEG in order to correctly display the
#         # video stream.
#         ret, jpeg = cv2.imencode('.jpg', image)
#         return jpeg.tobytes()

def main():
    print("----------- Main -----------")
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        if b'nginx.exe' not in subprocess.Popen('tasklist', stdout=subprocess.PIPE).communicate()[0]:
            print("Start nginx service!!")
            os.chdir('nginx-1.10.1')
            subprocess.Popen(
                ['nginx.exe'],
                shell = True,
                stdin = None,
                stdout = None,
                stderr = None,
                close_fds = True
            )
            os.chdir('..')
        else:
            print("Nginx already running!!")
    app.run(host = os.getenv('IP', "0.0.0.0"), port = int(os.getenv('PORT', 80)), threaded = True) #processes=1~9999
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        os.system("taskkill /f /im nginx.exe");
        print("End")

if __name__ == '__main__':
    main()