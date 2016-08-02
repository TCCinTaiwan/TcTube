# coding=utf-8
from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    Response,
    send_from_directory,
    make_response,
    stream_with_context,
    url_for,
    abort,
    flash,
    jsonify
)
from flask.ext.login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    current_user,
    logout_user,
    confirm_login,
    login_fresh,
    AnonymousUserMixin
)
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.compress import Compress
from flask_socketio import SocketIO, send, emit
from wtforms import form, fields, validators
from functools import wraps, partial
from werkzeug.security import generate_password_hash, check_password_hash
import binascii, os, re, json, random, subprocess, sqlite3, time, numpy, sys
from jinja2 import Environment, FileSystemLoader
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter
from functools import partial
from datetime import datetime
from urllib.parse import urlparse
import colorama
import requests
import platform

flaskApplication = Flask(__name__, static_url_path = "", static_folder = "static/", template_folder = 'templates/')
flaskApplication.debug = True
flaskApplication.config['FOLDER'] = os.getcwd()
flaskApplication.config['VIDEO_FOLDER'] = "file/video/"
flaskApplication.config['ALLOWED_EXTENSIONS'] = set([
    # "txt",
    # "pdf",
    # "png", "jpg", "jpeg", "gif",
    # "db",
    "mp3",
    "mp4", "webm", "ogg"
])
flaskApplication.config['PORT'] = 8000
flaskApplication.config['NGINX_FOLDER'] = 'nginx-1.10.1'
flaskApplication.config['NGINX_PORT'] = 80
flaskApplication.config['DATABASE_FILE'] = 'database.db'
flaskApplication.config["SECRET_KEY"] = "0" * 24 # binascii.hexlify(os.urandom(24))
flaskApplication.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + flaskApplication.config['DATABASE_FILE']
flaskApplication.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
socketio = SocketIO(flaskApplication, ping_timeout = 30, ping_interval = 30, binary=True)
sqlAlchemy = SQLAlchemy(flaskApplication)
login_manager = LoginManager()
colorama.init()
connection = {}

class classproperty(object):
    def __init__(self, getter):
        self.getter = getter
    def __get__(self, instance, owner):
        return self.getter(owner)

class JsonAPI(object):
    __public__ = None
    def api(self, rows):
        collection = []
        if self.__public__ != None:
            for row in rows:
                collection.append(row.serialize)
        return collection
    @property
    def serialize(self):
        def value(value):
            if (type(value) in [str, int, bool]):
                # A number (integer or floating point)
                # A string (in double quotes)
                # A Boolean (true or false)
                return value
            elif value:
                return self.api(value.all())
        if (type(self.__public__) == str):
            return value(getattr(self, self.__public__))
        elif (self.__public__ != None):
            dict = {}
            for public_key in self.__public__:
                dict[public_key] = value(getattr(self, public_key))
            return dict
    @classproperty
    def collection(cls):
        return cls.api(cls, cls.query.all())

class Announcement(sqlAlchemy.Model, JsonAPI):
    __tablename__ = 'announcements'
    __public__ = [
        "message"
    ]
    id = sqlAlchemy.Column(sqlAlchemy.Integer, primary_key = True, autoincrement = True)
    message = sqlAlchemy.Column(sqlAlchemy.String(64))
    def  __init__(self, message):
        self.message = message
    def __repr__(self):
        return '<Announcement %r>' % (self.id)

class Menu(sqlAlchemy.Model, JsonAPI):
    __tablename__ = 'menu'
    __public__ = [
        "parent_id",
        "name",
        "url",
        "title",
        "target",
        "onclick",
        "icon",
        "icon_open",
        "open"
    ]
    id = sqlAlchemy.Column(sqlAlchemy.Integer, primary_key = True, autoincrement = True)
    parent_id = sqlAlchemy.Column(sqlAlchemy.Integer)
    name = sqlAlchemy.Column(sqlAlchemy.String(64))
    url = sqlAlchemy.Column(sqlAlchemy.String(64))
    target = sqlAlchemy.Column(sqlAlchemy.String(64))
    title = sqlAlchemy.Column(sqlAlchemy.String(64))
    onclick = sqlAlchemy.Column(sqlAlchemy.String(64))
    icon = sqlAlchemy.Column(sqlAlchemy.String(64))
    icon_open = sqlAlchemy.Column(sqlAlchemy.String(64))
    open = sqlAlchemy.Column(sqlAlchemy.Boolean)
    def  __init__(self, parent_id, name, url, title,target, onclick, icon, icon_open, open):
        self.parent_id = parent_id
        self.name = name
        self.url = url
        self.title = title
        self.target = target
        self.onclick = onclick
        self.icon = icon
        self.icon_open = icon_open
        self.open = open
    def __repr__(self):
        return '<Menu %r>' % (self.name)

class Video(sqlAlchemy.Model, JsonAPI):
    __tablename__ = 'videos'
    __public__ = [
        "title",
        "artist",
        "thumbnail",
        "sources"
    ]
    id = sqlAlchemy.Column(sqlAlchemy.Integer, primary_key = True, autoincrement = True)
    title = sqlAlchemy.Column(sqlAlchemy.String(64))
    artist = sqlAlchemy.Column(sqlAlchemy.String(64))
    thumbnail = sqlAlchemy.Column(sqlAlchemy.String(64))
    sources = sqlAlchemy.relationship('VideoSource', backref = 'videos', lazy = 'dynamic')
    def  __init__(self, title, artist):
        self.title = title
        self.artist = artist
    def __repr__(self):
        return '<Video %r>' % (self.title)
class VideoSource(sqlAlchemy.Model, JsonAPI):
    __tablename__ = 'videoSources'
    __public__ = "source"
    id = sqlAlchemy.Column(sqlAlchemy.Integer, primary_key = True)
    video_id = sqlAlchemy.Column(sqlAlchemy.Integer, sqlAlchemy.ForeignKey('videos.id'), primary_key = True)
    source = sqlAlchemy.Column(sqlAlchemy.String(64))
    def  __init__(self, video_id, source):
        self.video_id = video_id
        self.source = source
    def __repr__(self):
        return '<VideoSource %r>' % (self.source)

class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.name = 'Guest'

class User(sqlAlchemy.Model):
    __tablename__ = 'users'
    COMPERENCE_ADMIN = 0
    COMPERENCE_USER = 10
    MIN_USERNAME_LEN = 3
    MAX_USERNAME_LEN = 20
    MIN_PASSWORD_LEN = 4
    MAX_PASSWORD_LEN = 40
    id = sqlAlchemy.Column(sqlAlchemy.Integer, primary_key = True, autoincrement = True)
    account = sqlAlchemy.Column(sqlAlchemy.String(64), index = True, unique = True)
    password_hash = sqlAlchemy.Column(sqlAlchemy.String(64))
    name = sqlAlchemy.Column(sqlAlchemy.String(64))
    email = sqlAlchemy.Column(sqlAlchemy.String(120), index = True, unique = True)
    affiliation = sqlAlchemy.Column(sqlAlchemy.Integer)
    phone = sqlAlchemy.Column(sqlAlchemy.String(64), nullable = True)
    birthday = sqlAlchemy.Column(sqlAlchemy.Date, nullable = True)
    creating_time = sqlAlchemy.Column(sqlAlchemy.DateTime, default = datetime.utcnow(), nullable=True)
    login_time = sqlAlchemy.Column(sqlAlchemy.DateTime, default = datetime.utcnow(), nullable=True)
    login_ip = sqlAlchemy.Column(sqlAlchemy.String(32), nullable = True)
    competence = sqlAlchemy.Column(sqlAlchemy.Integer, default = COMPERENCE_USER)
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, account, password, name, email, affiliation = None, creating_time = None, login_time = None, competence = COMPERENCE_USER, birthday = None, phone = None):
        self.account = account
        self.password_hash = generate_password_hash(password)
        self.name = name
        self.email = email
        self.affiliation = affiliation
        if phone is not None:
            self.phone = phone
        if birthday is not None:
            self.birthday = birthday
        if creating_time is None:
            creating_time = datetime.utcnow()
        self.creating_time = creating_time
        if login_time is None:
            login_time = datetime.utcnow()
        self.login_time = login_time
        self.competence = competence

    def __repr__(self):
        return '<User %r>' % (self.name)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @classmethod
    def getByAccount(cls, account):
        return cls.query.filter_by(account = account).first()

    @classmethod
    def get(cls,id):
        return cls.query.filter_by(id = id).first()

# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    account = fields.TextField("帳號", validators = [validators.required()])
    password = fields.PasswordField("密碼",
        [
            validators.Length(
                min = User.MIN_PASSWORD_LEN,
                max= User.MAX_PASSWORD_LEN
            )
        ])
    submit = fields.SubmitField("登入", render_kw = {"class": "123"})
class LogoutForm(form.Form):
    submit = fields.SubmitField("登出")

class SignupForm(form.Form):
    account   = fields.TextField(
        'Account',
        [
            validators.Length(
                min = User.MIN_USERNAME_LEN,
                max = User.MAX_USERNAME_LEN
            ),
            validators.Regexp(
                "^[a-zA-Z0-9]*$",
                message = "Username can only contain letters and numbers"
            )
        ]
    )
    name = fields.TextField(
        'Name',
        [
            validators.Required()
        ]
    )
    email = fields.TextField(
        'Email',
        [
            validators.Required(),
            validators.Email()
        ]
    )
    password = fields.PasswordField(
        'New Password',
        [
            validators.Length(
                min = User.MIN_PASSWORD_LEN,
                max= User.MAX_PASSWORD_LEN
            )
        ]
    )
    confirm = fields.PasswordField(
        'Repeat Password',
        [
            validators.Required(),
            validators.EqualTo(
                'password',
                message = 'Passwords must match'
            )
        ]
    )
    submit = fields.SubmitField("Send")

@flaskApplication.before_request
def check_login():
    if request.remote_addr != "127.0.0.1":
        return redirect("/", code = 302)
    # if request.endpoint == 'static' and not current_user.is_authenticated:
    #     return render_template('error.htm', title = "Forbidden",error = "權限不足", redirect = "/", redirectTime = 100), 403
    return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@login_manager.header_loader
def load_user_from_header(header_val):
    header_val = header_val.replace('Basic ', '', 1)
    try:
        header_val = base64.b64decode(header_val)
    except TypeError:
        pass
    return User.query.filter_by(api_key = header_val).first()

@login_manager.unauthorized_handler
def unauthorized():
    flash('請登入再繼續')
    next = urlparse(request.url).path
    return redirect(url_for('login', next = next))
# login_manager.login_view = "login"

# @login_manager.request_loader
# def load_user(request):
#     token = request.headers.get('Authorization')
#     if token is None:
#         token = request.args.get('token')

#     if token is not None:
#         account, password = token.split(":") # naive token
#         user = User.getByAccount(account)
#         if (user.password == password):
#             return user
#     return None

@flaskApplication.after_request
def add_header(response):
    # print(colorama.Fore.GREEN + current_user.name + colorama.Fore.RESET)
    response.cache_control.max_age = 300
    return response

def stream_tmeplate(template_name, **context):
    flaskApplication.update_template_context(context)
    template = flaskApplication.jinja_env.get_template(template_name)
    templateStream = template.stream(context)
    templateStream.enable_buffering(5)
    return templateStream

@flaskApplication.context_processor
def utility_processor():
    def splitFilename(filename):
        return os.path.splitext(filename)
    return dict(splitFilename = splitFilename)

def TestPlatform():
    print ("---------- Operation System ----------")
    #  获取Python版本
    print(platform.python_version())

    #   获取操作系统可执行程序的结构，，(’32bit’, ‘WindowsPE’)
    print(platform.architecture())

    #   计算机的网络名称，’acer-PC’
    print(platform.node())

    #获取操作系统名称及版本号，’Windows-7-6.1.7601-SP1′
    print(platform.platform())

    #计算机处理器信息，’Intel64 Family 6 Model 42 Stepping 7, GenuineIntel’
    print(platform.processor())

    # 获取操作系统中Python的构建日期
    print(platform.python_build())

    #  获取系统中python解释器的信息
    print(platform.python_compiler())

    if platform.python_branch() == "":
        print(platform.python_implementation())
        print(platform.python_revision())
    print(platform.release())
    print(platform.system())

    #  获取操作系统的版本
    print(platform.version())

    #  包含上面所有的信息汇总
    print(platform.uname())

'''
Get current time as milliseconds since 1970-01-01
'''
def dates():
    return int(time.mktime(datetime.utcnow().timetuple())) * 1000

def getRealIP(request):
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    else:
        return request.remote_addr

# 裝飾
def access_permission(func = None, level = None):
    if not func:
        return partial(access_permission, level = level)
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('%s[%s]%s%s%s, user = %s, Requirelevel = %d' % (colorama.Fore.MAGENTA, datetime.utcnow(), colorama.Fore.GREEN, func.__name__, colorama.Style.RESET_ALL, current_user.name, level if level != None else -1))
        if current_user.competence > level:
            return render_template('error.htm', title = "Forbidden",error = "權限不足", redirect = "/", redirectTime = 100), 403
        return func(*args, **kwargs)
    return wrapper

@flaskApplication.route('/')
@login_required
@access_permission(level = 10)
def index():
    announcements = Announcement.query.all()
    menu = Menu.query.all()
    videos = sqlAlchemy.session.query(Video)
    return render_template("index.htm", title = 'Index', announcements = announcements, menu = menu, videos = videos, Video = Video)

@flaskApplication.route("/listUser/")
@login_required
@access_permission(level = 5)
def listUser():
    announcements = Announcement.query.all()
    menu = Menu.query.all()
    users = User.query.filter(User.competence > current_user.competence)
    return render_template('listUser.htm', title = "List Users", users = users, announcements = announcements, menu = menu)

@flaskApplication.route("/announcements/")
@login_required
@access_permission(level = 5)
def announcements():
    menu = Menu.query.all()
    announcements = sqlAlchemy.session.query(Announcement).all()
    return render_template('announcements.htm', title = "Announcements", announcements = announcements, menu = menu)

@flaskApplication.route('/video/')
def randomVideo(): # 隨機Video
    # with open('static/playlist.json', "r", encoding = 'utf8') as jsonFile:
    #     jsonData = json.load(jsonFile)
    videos = random.randrange(len(sqlAlchemy.session.query(Video).all()))
    return redirect("/video/" + str(videos), code = 301)

@flaskApplication.route('/video/<int:videoNum>')
@login_required
@access_permission(level = 10)
def video(videoNum):
    menu = Menu.query.all()
    videos = sqlAlchemy.session.query(Video)
    announcements = Announcement.query.all()
    return render_template('video.htm', videoNum = videoNum, videos = videos, announcements = announcements, menu = menu)

@flaskApplication.route('/api/')
def api():
    return jsonify(video = Video.collection, menu = Menu.collection, announcement = Announcement.collection)

@flaskApplication.route("/api/debug/")
@login_required
@access_permission(level = 1)
def debug():
    tempdict = {}
    for key in request.environ:
         if type(request.environ[key]) in [int, str, bool]:
            tempdict[key] = request.environ[key]
    return jsonify(tempdict)


@flaskApplication.route("/api/online/")
def online():
    return jsonify(connection)

@flaskApplication.route('/list/')
def listRoot():
    return list("")
@flaskApplication.route('/list/<string:path>/')
@login_required
@access_permission(level = 5)
def list(path):
    def formattime(time):
        return datetime.strftime(
            datetime.fromtimestamp(time),
            '%Y-%m-%d %H:%M:%S'
        )
    files = []
    folderpath = os.path.join(flaskApplication.config['VIDEO_FOLDER'] , path)
    path = "/" + path
    for index, file in enumerate(os.listdir(folderpath)):
        filepath = os.path.join(folderpath, file)
        relativepath = os.path.join(path, file)
        files.append({
            "index": index,
            "name": file,
            "url": ("/view" if (os.path.isfile(filepath)) else "/list") + relativepath,
            "download_url": "/" + flaskApplication.config['VIDEO_FOLDER'][:-1] + relativepath,
            "type": "file" if os.path.isfile(filepath) else "folder" if os.path.isdir(filepath) else "unknown",
            "mtime": formattime(os.path.getmtime(filepath)),
            "ctime": formattime(os.path.getctime(filepath)),
            "atime": formattime(os.path.getatime(filepath)),
            "size": os.path.getsize(filepath)
        })
    announcements = Announcement.query.all()
    menu = Menu.query.all()
    return render_template("list.htm", title = 'List', files = files, folderpath = path, announcements = announcements, menu = menu)
# def mimetype(filepath):
#     return magic.from_file(filepath)

@flaskApplication.route('/view/<path:path>') # 強制檢視影片，而不是看瀏覽器而下載或觀看
@login_required
def view(path):
    announcements = Announcement.query.all()
    menu = Menu.query.all()
    absolutePath = re.match(r"^http(s|)://[^/:]{1,}", request.url).group(0)
    return render_template('viewMedia.htm', mediaFile = absolutePath + ":" + str(flaskApplication.config['NGINX_PORT']) + "/" + flaskApplication.config['VIDEO_FOLDER'] + path)

@flaskApplication.route('/signup/')
def signup():
    form = SignupForm(request.form)
    return render_template('signup.htm', title = "Sign Up", form = form)

@flaskApplication.route('/login/', methods = ['GET','POST'])
def login():
    form = LoginForm(request.form)
    if form.validate(): # request.method == 'POST':
        user = User.getByAccount(form.account.data)
        if user:
            if (user.verify_password(form.password.data)):
                user.authenticated = True
                user.login_time = datetime.utcnow()
                user.login_ip = getRealIP(request)
                sqlAlchemy.session.add(user)
                sqlAlchemy.session.commit()
                login_user(user, remember = True)
                next = request.args.get('next')
                flash('Logged in successfully.')
                return redirect(next or url_for("index"))
    if current_user != Anonymous:
        return redirect("/")

    return render_template('login.htm', title = "Login", form = form)

# @flaskApplication.route('/proxy/<path:url>')
# def proxy(url):
#     url = 'http://%s' % url
#     req = requests.get(url, stream = True, params = request.args)
#     return Response(stream_with_context(req.iter_content(1024)), content_type = req.headers['content-type'])

@flaskApplication.route('/logout/', methods = ['POST'])
@login_required
def logout():
    logout_user()
    next = request.args.get('next')
    return redirect(next or url_for("index"))

@flaskApplication.route('/upload/', methods = ['GET','POST']) # 上傳檔案
@login_required
@access_permission(level = 5)
def upload_file():
    if (request.method == 'POST'):
        files = request.files.getlist('files[]')
        uploadFilesStatus = []
        for file in files:
            filename = file.filename
            if allowed_file(filename):
                print("Uploaded a File!!")
                filename = filename_filter(filename)
                file.save(os.path.join(flaskApplication.config['VIDEO_FOLDER'], filename))
                uploadFilesStatus.append((0, filename)) # 0: success
            else:
                print("Unsupported File Type!!")
                uploadFilesStatus.append((1, "Unsupported File Type")) # 1: failed
        successFiles = [info for status, info  in uploadFilesStatus if status == 0]
        return "<h2>上傳" + str(len(files)) + "個檔案中，成功" + str(len(successFiles)) + "個檔案</h2><p>" + "</p><p>".join(successFiles) + "</p>"
    announcements = Announcement.query.all()
    menu = Menu.query.all()
    return render_template('upload.htm', title = 'Upload', announcements = announcements, menu = menu)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1] in flaskApplication.config['ALLOWED_EXTENSIONS']
def filename_filter(filename):
    # filename = re.sub('[" "\/\--]+', '-', filename)
    # filename = re.sub(r':-', ':', filename)
    # filename = re.sub(r'^-|-$', '', filename)
    return filename

@flaskApplication.route("/file/<path:path>") # 轉址到nginx伺服器
def media(path):
    mediaFileUrl = re.sub(r"(:[0-9]{0,}|)/file/", ":" + str(flaskApplication.config['NGINX_PORT']) + "/file/", request.url) # nginx port
    return redirect(mediaFileUrl, code = 302)

@socketio.on('connect', namespace = '/test')
def socketio_connect():
    connection[request.sid] = {
        "ip": getRealIP(request),
        "name": current_user.name
    }
    emit('hello', connection[request.sid], broadcast = True)

@socketio.on('disconnect')
def socketio_disconnect():
    del connection[request.sid]

@socketio.on('PauseVideo', namespace = '/test')
@login_required
@access_permission(level = 5)
def pasue_video(message):
    emit('pause', {
        "time": dates() + message['delay']
    }, broadcast = True)

@socketio.on('PushVideo', namespace = '/test')
@login_required
@access_permission(level = 5)
def test_message(message):
    emit('redirect', {
        "url": "/video/" + str(numpy.clip(int(message['id']), 0, len(sqlAlchemy.session.query(Video).all()) - 1)),
        "time": dates() + message['delay']
    }, broadcast = True)

@socketio.on('HideAnnouncements', namespace = '/test')
@login_required
@access_permission(level = 5)
def hide_announcements(message):
    emit('hideAnnouncements', {}, broadcast = True)

if __name__ == '__main__':
    TestPlatform()
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        if (os.name == "nt"):
            nginxRunning = b'nginx' in subprocess.Popen(
                'tasklist',
                stdout = subprocess.PIPE
            ).communicate()[0]
            if (not nginxRunning):
                print(colorama.Fore.YELLOW + "Start nginx service!!" + colorama.Style.RESET_ALL)
                os.chdir(flaskApplication.config['NGINX_FOLDER'])
                subprocess.Popen(
                    ['nginx.exe'],
                    shell = True,
                    stdin = None,
                    stdout = None,
                    stderr = None,
                    close_fds = True
                )
                os.chdir(flaskApplication.config['FOLDER'])
            else:
                print(colorama.Fore.GREEN + "Nginx is already running!!" + colorama.Style.RESET_ALL)
        elif (os.name == "posix"):
            nginxRunning = b'active' in subprocess.Popen(
                [
                    '/etc/init.d/nginx',
                    'status'
                ],
                stdout = subprocess.PIPE
            ).communicate()[0]
            if (not nginxRunning):
                print(colorama.Fore.YELLOW + "Start nginx service!!" + colorama.Style.RESET_ALL)
                os.system(("sudo /etc/init.d/nginx start")
            else:
                print(colorama.Fore.GREEN + "Nginx is already running!!" + colorama.Style.RESET_ALL)
    Compress(flaskApplication)
    login_manager.init_app(flaskApplication)
    login_manager.session_protection = "strong"
    login_manager.anonymous_user = Anonymous
    print(colorama.Fore.GREEN + "----------- Start Flask -----------" + colorama.Style.RESET_ALL)
    socketio.run(flaskApplication, host = os.getenv('IP', "0.0.0.0"), port = int(os.getenv('PORT', flaskApplication.config['PORT'])))
    # flaskApplication.run(host = os.getenv('IP', "0.0.0.0"), port = int(os.getenv('PORT', flaskApplication.config['PORT'])), threaded = True) #processes=1~9999
    socketio.emit("bye", broadcast = True)
    print(colorama.Fore.RED + "----------- Stop Flask -----------" + colorama.Style.RESET_ALL)
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        if (os.name == "nt"):
            os.system("taskkill /f /im nginx.exe")
            nginxRunning = b'nginx' in subprocess.Popen(
                'tasklist',
                stdout = subprocess.PIPE
            ).communicate()[0]
            if (not nginxRunning):
                print(colorama.Fore.RED + "Stop nginx service!!" + colorama.Style.RESET_ALL)
            else:
                print(colorama.Fore.YELLOW + "Nginx is still running!!" + colorama.Style.RESET_ALL)
        elif (os.name == "posix"):
            os.system("sudo /etc/init.d/nginx stop")
            nginxRunning = b'active' in subprocess.Popen(
                [
                    '/etc/init.d/nginx',
                    'status'
                ],
                stdout = subprocess.PIPE
            ).communicate()[0]
            if (not nginxRunning):
                print(colorama.Fore.RED + "Stop nginx service!!" + colorama.Style.RESET_ALL)
            else:
                print(colorama.Fore.YELLOW + "Nginx is still running!!" + colorama.Style.RESET_ALL)