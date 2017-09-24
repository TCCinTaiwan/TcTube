# coding=utf-8
# 載入Flask函式庫
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
# 載入Flask Login函式庫
from flask_login import (
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
# 載入Flask資料庫函式庫
from flask_sqlalchemy import SQLAlchemy
# 載入Falsk壓縮函式庫
from flask_compress import Compress
# 載入以Flask實現的SocketIO函式庫
from flask_socketio import SocketIO, send, emit, disconnect
from wtforms import form, fields, validators
# 用來搭配Python裝飾使用
from functools import wraps, partial
from werkzeug.security import generate_password_hash, check_password_hash
import binascii, os, re, json, random, subprocess, sqlite3, time, numpy, sys
# 載入時間函式庫
from datetime import datetime
# 匯入urlparse，用來分解請求網址
from urllib.parse import urlparse
# 載入colorma模組，用來改變終端機文字輸出樣式
import colorama
# 載入requests模組，用來製作Proxy
import requests
# 載入platform模組，可以用來獲取系統訊息
import platform
import logging
from logging.handlers import RotatingFileHandler
# raise ImportError('Try "python setup.py install" or "pip install -r requirements.txt"')


flaskApplication = Flask(__name__, static_url_path = "", static_folder = "static/", template_folder = 'templates/')
flaskApplication.debug = False
flaskApplication.config['FOLDER'] = os.getcwd()
flaskApplication.config['VIDEO_FOLDER'] = "file/video/"
flaskApplication.config['VIDEO_THUMBNAIL_FOLDER'] = "/file/image/streamshot/"
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
socketio = SocketIO(flaskApplication, async_mode = "eventlet", ping_timeout = 20, ping_interval = 0, binary = True) # , ping_timeout = 30, ping_interval = 30, binary = True
sqlAlchemy = SQLAlchemy(flaskApplication)
login_manager = LoginManager()
colorama.init()
connection = {}

# 定義類別屬性
class classproperty(object):
    def __init__(self, getter):
        self.getter = getter
    def __get__(self, instance, owner):
        return self.getter(owner)

# 資料庫轉Json格式的API
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

# 資料庫公告
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

# 資料庫選單
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

# 資料庫影片
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

# 資料庫影片來源
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

# 資料庫使用者
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
    connect_time = sqlAlchemy.Column(sqlAlchemy.DateTime, default = datetime.utcnow(), nullable=True)
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

    def __init__(self, account, password, name, email, affiliation = None, creating_time = None, login_time = None, connect_time = None, competence = COMPERENCE_USER, birthday = None, phone = None):
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
        if connect_time is None:
            connect_time = datetime.utcnow()
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

# 定義登入表單
class LoginForm(form.Form):
    account = fields.TextField(
        "帳號",
        validators = [
            validators.required()
        ]
    )
    password = fields.PasswordField(
        "密碼",
        [
            validators.Length(
                min = User.MIN_PASSWORD_LEN,
                max= User.MAX_PASSWORD_LEN
            )
        ]
    )
    submit = fields.SubmitField("登入", render_kw = {"class": "123"})

# 定義登出表單
class LogoutForm(form.Form):
    submit = fields.SubmitField("登出")

# 定義註冊表單
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

# 預先檢查，可用來檢測Flask靜態檔案權限
@flaskApplication.before_request
def check_login():
    # if request.remote_addr != "127.0.0.1": # 規定必須用Nginx的Proxy
    #     return redirect(url_for("/"), code = 302)
    # if request.endpoint == 'static' and not current_user.is_authenticated:
    #     return render_template('error.htm', title = "Forbidden",error = "權限不足", redirect = "/", redirectTime = 100), 403
    return None

# 回傳當前使用者
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# @login_manager.header_loader
# def load_user_from_header(header_val):
#     header_val = header_val.replace('Basic ', '', 1)
#     try:
#         header_val = base64.b64decode(header_val)
#     except TypeError:
#         pass
#     return User.query.filter_by(api_key = header_val).first()

# 登入確認
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

# @flaskApplication.after_request
# def add_header(response):
#     # print(colorama.Fore.GREEN + current_user.name + colorama.Fore.RESET)
#     response.cache_control.max_age = 300
#     return response

# 串流樣板
def stream_tmeplate(template_name, **context):
    flaskApplication.update_template_context(context)
    template = flaskApplication.jinja_env.get_template(template_name)
    templateStream = template.stream(context)
    templateStream.enable_buffering(5)
    return templateStream

# 樣板預處理
@flaskApplication.context_processor
def utility_processor():
    def splitFilename(filename):
        return os.path.splitext(filename)
    def absoluteOrRelative(url = "", baseUrl = None):
        if ("http://" in url[:7] or "https://" in url[:8]):
            return url
        if (baseUrl == None):
            baseUrl = urlparse(request.url).scheme
        return baseUrl + url
    return dict(splitFilename = splitFilename, absoluteOrRelative = absoluteOrRelative)


'''
Get current time as milliseconds since 1970-01-01
'''
def dates(customDate = None, isUTC = False):
    if (customDate == None):
        return int((time.time() + time.timezone) * 1000) # time.mktime(time.gmtime())
    else:
        return int((time.mktime(customDate.timetuple()) + (time.timezone if isUTC else 0)) * 1000)

# 真實IP(Proxy沒隱藏的話)
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

@flaskApplication.route('/', methods = ['GET','POST'])
@login_required
@access_permission(level = 10)
def index():
    announcements = Announcement.query.all()
    menu = Menu.query.all()
    videos = None
    # videos = sqlAlchemy.session.query(Video).filter(Video.title.like("%" + request.form.query.data + "%")).all()
    videos = sqlAlchemy.session.query(Video).all()
    return render_template("index.htm", title = 'Index', announcements = announcements, menu = menu, videos = videos, Video = Video, thumbnail_folder = flaskApplication.config['VIDEO_THUMBNAIL_FOLDER'])

# 列出層級比當前使用者低的使用者
@flaskApplication.route("/listUser/")
@login_required
@access_permission(level = 5)
def listUser():
    announcements = Announcement.query.all()
    menu = Menu.query.all()
    users = User.query.filter(User.competence > current_user.competence)
    return render_template('listUser.htm', title = "List Users", users = users, announcements = announcements, menu = menu)

# 管理公告
@flaskApplication.route("/announcements/")
@login_required
@access_permission(level = 5)
def announcements():
    menu = Menu.query.all()
    announcements = sqlAlchemy.session.query(Announcement).all()
    return render_template('announcements.htm', title = "Announcements", announcements = announcements, menu = menu)

# @flaskApplication.route("/announcement/<int:id>")
# @login_required
# @access_permission(level = 5)
# def announcement(id):
#     menu = Menu.query.all()
#     announcements = sqlAlchemy.session.query(Announcement).all()
#     return render_template('announcement.htm', title = "Announcement", announcements = announcements, menu = menu)

# 管理選單
@flaskApplication.route("/menu/")
@login_required
@access_permission(level = 5)
def menu():
    menu = Menu.query.all()
    announcements = sqlAlchemy.session.query(Announcement).all()
    return render_template('menu.htm', title = "Menu", announcements = announcements, menu = menu)

# 聊天室
@flaskApplication.route("/chat/")
@login_required
def socketIO():
    menu = Menu.query.all()
    announcements = sqlAlchemy.session.query(Announcement).all()
    return render_template('chat.htm', title = "Chat", announcements = announcements, menu = menu)

@flaskApplication.route('/video/')
def randomVideo(): # 隨機Video
    # with open('static/playlist.json', "r", encoding = 'utf8') as jsonFile:
    #     jsonData = json.load(jsonFile)
    videos = random.randrange(len(sqlAlchemy.session.query(Video).all()))
    return redirect("/video/" + str(videos), code = 302)

# 指定播放影片編號
@flaskApplication.route('/video/<int:videoNum>')
@login_required
@access_permission(level = 10)
def video(videoNum):
    menu = Menu.query.all()
    videos = sqlAlchemy.session.query(Video)
    announcements = Announcement.query.all()
    return render_template('video.htm', videoNum = videoNum, videos = videos, announcements = announcements, menu = menu)

# 列出影片、選單跟公告的Json
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

# 列出Socket IO連線使用者
@flaskApplication.route("/api/online/")
def online():
    return jsonify(connection)

# 列出影片資料夾
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

# 強制檢視影片，而不是看瀏覽器而下載或觀看
@flaskApplication.route('/view/<path:path>')
@login_required
def view(path):
    announcements = Announcement.query.all()
    menu = Menu.query.all()
    absolutePath = re.match(r"^http(s|)://[^/:]{1,}", request.url).group(0)
    return render_template('viewMedia.htm', mediaFile = absolutePath + ":" + str(flaskApplication.config['NGINX_PORT']) + "/" + flaskApplication.config['VIDEO_FOLDER'] + path)

# 註冊(沒做回傳)
# @flaskApplication.route('/signup/')
# def signup():
#     form = SignupForm(request.form)
#     return render_template('signup.htm', title = "Sign Up", form = form)

# 登入
@flaskApplication.route('/login/', methods = ['GET','POST'])
def login():
    form = LoginForm(request.form)
    if current_user.is_authenticated:
        return redirect("/")
    if form.validate(): # request.method == 'POST':
        user = User.getByAccount(form.account.data)
        if user:
            # user.password = form.password.data
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
    return render_template('login.htm', title = "Login", form = form)

# @flaskApplication.route('/proxy/<path:url>')
# def proxy(url):
#     url = 'http://%s' % url
#     req = requests.get(url, stream = True, params = request.args)
#     return Response(stream_with_context(req.iter_content(1024)), content_type = req.headers['content-type'])

# 登出
@flaskApplication.route('/logout/', methods = ['POST'])
@login_required
def logout():
    logout_user()
    next = request.args.get('next')
    return redirect(next or url_for("index"))

# 上傳檔案
@flaskApplication.route('/upload/', methods = ['GET','POST']) # 上傳檔案
@login_required
@access_permission(level = 5)
def upload_file():
    announcements = Announcement.query.all()
    menu = Menu.query.all()
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
        return render_template('uploadSuccess.htm', title = 'Upload Success', announcements = announcements, menu = menu, successFiles = successFiles, files = files)
    return render_template('upload.htm', title = 'Upload', announcements = announcements, menu = menu)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1] in flaskApplication.config['ALLOWED_EXTENSIONS']
def filename_filter(filename):
    # filename = re.sub('[" "\/\--]+', '-', filename)
    # filename = re.sub(r':-', ':', filename)
    # filename = re.sub(r'^-|-$', '', filename)
    return filename

# 轉址到nginx伺服器
@flaskApplication.route("/file/<path:path>")
def media(path):
    mediaFileUrl = re.sub(r"(:[0-9]{0,}|)/file/", ":" + str(flaskApplication.config['NGINX_PORT']) + "/file/", request.url) # nginx port
    return redirect(mediaFileUrl, code = 302)

@socketio.on_error(namespace = '/test')
def error_handler_chat(e):
    print(e)

@socketio.on('typing', namespace = '/test')
def socketio_chat_typing(message):
    emit('typing', {
        'name': connection[getRealIP(request)][request.sid]["name"],
    }, broadcast = True)

@socketio.on('stop typing', namespace = '/test')
def socketio_chat_stop_typing(message):
    emit('stop_typing', {
        'name': connection[getRealIP(request)][request.sid]["name"],
    }, broadcast = True)



@socketio.on('test ping', namespace = '/test')
def socketio_test_ping():
    emit('test pong')

@socketio.on('get path', namespace = '/test')
def socketio_get_path(data):
    connection[getRealIP(request)][request.sid]["path"] = data["path"]

@socketio.on('report ping', namespace = '/test')
def socketio_test_pong(data):
    connection[getRealIP(request)][request.sid]["ping2"] = data["ping"]

@socketio.on('test pong', namespace = '/test')
def socketio_test_pong():
    connection[getRealIP(request)][request.sid]["ping"] = dates() - connection[getRealIP(request)][request.sid]["ping_time"]
    del connection[getRealIP(request)][request.sid]["ping_time"]
def socketio_server_ping_client():
    connection[getRealIP(request)][request.sid]["ping_time"] = dates()
    emit('test ping')

@socketio.on('connect', namespace = '/test')
def socketio_connect():
    realIP = getRealIP(request)
    connectTime = datetime.utcnow()
    print("Connect: ", realIP)
    sqlAlchemy.session.commit()
    if realIP not in connection:
        connection[realIP] = {}
    connection[realIP][request.sid] = {
        "ip": realIP
    }

    if (current_user.is_authenticated):
        current_user.connect_time = connectTime
        connection[realIP][request.sid].update(
            {
                "login_ip": current_user.login_ip,
                "login_time": dates(current_user.login_time, isUTC = True),
                "name": current_user.name,
                "account": current_user.account,
                "connect_time": dates(current_user.connect_time, isUTC = True)
            }
        )
    emit('connect success', connection[realIP][request.sid])
    emit('user online', connection[realIP][request.sid], broadcast = True)
    socketio_server_ping_client()

@socketio.on('disconnect', namespace = '/test')
def socketio_disconnect():
    realIP = getRealIP(request)
    print("Disconnect: ", realIP)
    emit('user left', connection[realIP][request.sid], broadcast = True)
    del connection[realIP][request.sid]

@socketio.on('new message', namespace = '/test')
def socketio_new_message(message):
    emit('new message', {
        'name': connection[getRealIP(request)][request.sid]["name"],
        'message': message
    }, broadcast = True)

@socketio.on('report play history', namespace = '/test')
def socketio_report_play_history(data):
    print(colorama.Fore.RED + str(data) + colorama.Style.RESET_ALL)

@socketio.on('disconnect request', namespace = '/test')
def disconnect_request():
    # emit('user left', connection[getRealIP(request)][request.sid], broadcast = True)
    # del connection[getRealIP(request)][request.sid]
    disconnect()

@socketio.on('PauseVideo', namespace = '/test')
@login_required
@access_permission(level = 5)
def pasue_video(message):
    emit(
        'pause',
        {
            "time": dates() + message['delay']
        },
        broadcast = True
    )

@socketio.on('PushVideo', namespace = '/test')
@login_required
@access_permission(level = 5)
def test_message(message):
    emit(
        'url redirect',
        {
            "url": "/video/" + str(numpy.clip(int(message['id']), 0, len(sqlAlchemy.session.query(Video).all()) - 1)),
            "time": dates() + message['delay']
        },
        broadcast = True
    )

if __name__ == '__main__':
    # 啟動nginx
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
            nginxRunning = b'Active: active' in subprocess.Popen(
                [
                    '/etc/init.d/nginx',
                    'status'
                ],
                stdout = subprocess.PIPE
            ).communicate()[0]
            if (not nginxRunning):
                print(colorama.Fore.YELLOW + "Start nginx service!!" + colorama.Style.RESET_ALL)
                os.system("sudo /etc/init.d/nginx start")
            else:
                print(colorama.Fore.GREEN + "Nginx is already running!!" + colorama.Style.RESET_ALL)

    Compress(flaskApplication)
    login_manager.init_app(flaskApplication)
    login_manager.session_protection = "strong"
    # login_manager.anonymous_user = Anonymous
    # formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
    # handler = logging.handlers.RotatingFileHandler('access.log', maxBytes = 100000, backupCount = 3)
    # handler.setLevel(logging.INFO)
    # handler.setFormatter(formatter)
    # flaskApplication.logger.addHandler(handler)
    # flaskApplication.logger.warning('A warning occurred (%d apples)', 42)
    # flaskApplication.logger.error('An error occurred')
    # flaskApplication.logger.info('Info')
    print(colorama.Fore.GREEN + "----------- Start Flask -----------" + colorama.Style.RESET_ALL)
    # flaskApplication.run(host = os.getenv('IP', "0.0.0.0"), port = int(os.getenv('PORT', flaskApplication.config['PORT'])), threaded = True) #processes=1~9999
    socketio.run(flaskApplication, host = os.getenv('IP', "0.0.0.0"), port = int(os.getenv('PORT', flaskApplication.config['PORT'])), debug = flaskApplication.debug)
    # socketio.emit("bye", broadcast = True)
    print(colorama.Fore.RED + "----------- Stop Flask -----------" + colorama.Style.RESET_ALL)

    # 關閉nginx
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
            nginxRunning = b'Active: active' in subprocess.Popen(
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