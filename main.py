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
    login_fresh
)
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.compress import Compress
from flask_socketio import SocketIO, send, emit
from wtforms import form, fields, validators
from functools import wraps, partial
from werkzeug.security import generate_password_hash, check_password_hash
import binascii, os, re, json, random, subprocess, sqlite3
from jinja2 import Environment, FileSystemLoader
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter
from functools import partial
from datetime import datetime
from urllib.parse import urlparse
app = Flask(__name__, static_url_path = "", static_folder = "static/")
app.debug = True
app.config['VIDEO_FOLDER'] = "media/video/"
app.config['ALLOWED_EXTENSIONS'] = set([
    # "txt",
    # "pdf",
    # "png", "jpg", "jpeg", "gif",
    # "db",
    "mp3",
    "mp4", "webm", "ogg"
])
app.config['NGINX_FOLDER'] = 'nginx-1.10.1'
app.config['NGINX_PORT'] = 8000
app.config['DATABASE_FILE'] = 'database.db'
app.config["SECRET_KEY"] = "0" * 24 # binascii.hexlify(os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
socketio = SocketIO(app)
Compress(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"


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

class Announcement(db.Model, JsonAPI):
    __tablename__ = 'announcements'
    __public__ = [
        "message"
    ]
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    message = db.Column(db.String(64))
    def  __init__(self, message):
        self.message = message
    def __repr__(self):
        return '<Announcement %r>' % (self.id)
class Menu(db.Model, JsonAPI):
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
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    parent_id = db.Column(db.Integer)
    name = db.Column(db.String(64))
    url = db.Column(db.String(64))
    target = db.Column(db.String(64))
    title = db.Column(db.String(64))
    onclick = db.Column(db.String(64))
    icon = db.Column(db.String(64))
    icon_open = db.Column(db.String(64))
    open = db.Column(db.Boolean)
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
class Video(db.Model, JsonAPI):
    __tablename__ = 'videos'
    __public__ = [
        "title",
        "artist",
        "sources"
    ]
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(64))
    artist = db.Column(db.String(64))
    thumbnail = db.Column(db.String(64))
    sources = db.relationship('VideoSource', backref = 'videos', lazy = 'dynamic')
    def  __init__(self, title, artist):
        self.title = title
        self.artist = artist
    def __repr__(self):
        return '<Video %r>' % (self.title)
class VideoSource(db.Model, JsonAPI):
    __tablename__ = 'videoSources'
    __public__ = "source"
    id = db.Column(db.Integer, primary_key = True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), primary_key = True)
    source = db.Column(db.String(64))
    def  __init__(self, video_id, source):
        self.video_id = video_id
        self.source = source
    def __repr__(self):
        return '<VideoSource %r>' % (self.source)

class User(db.Model):
    __tablename__ = 'users'
    COMPERENCE_ADMIN = 0
    COMPERENCE_USER = 10
    MIN_USERNAME_LEN = 3
    MAX_USERNAME_LEN = 20
    MIN_PASSWORD_LEN = 4
    MAX_PASSWORD_LEN = 40
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    account = db.Column(db.String(64), index = True, unique = True)
    password_hash = db.Column(db.String(64))
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), index = True, unique = True)
    affiliation = db.Column(db.Integer)
    phone = db.Column(db.String(64), nullable = True)
    birthday = db.Column(db.Date, nullable = True)
    creating_time = db.Column(db.DateTime, default = datetime.utcnow(), nullable=True)
    login_time = db.Column(db.DateTime, default = datetime.utcnow(), nullable=True)
    login_ip = db.Column(db.String(32), nullable = True)
    competence = db.Column(db.Integer, default = COMPERENCE_USER)
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

@app.before_request
def check_login():
    # print([item for item in current_user])
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

@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response

def stream_tmeplate(template_name, **context):
    app.update_template_context(context)
    template = app.jinja_env.get_template(template_name)
    templateStream = template.stream(context)
    templateStream.enable_buffering(5)
    return templateStream

@app.context_processor
def utility_processor():
    def splitFilename(filename):
        return os.path.splitext(filename)
    return dict(splitFilename = splitFilename)

# 裝飾
def access_permission(func = None, level = None):
    if not func:
        return partial(access_permission, level = level)
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('[%s] 呼叫 %s(), user = %s, level = %d' % (datetime.utcnow(), func, current_user, level if level != None else -1))
        if current_user.competence > level:
            return render_template('error.htm', title = "Forbidden",error = "權限不足", redirect = "/", redirectTime = 100), 403
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
@login_required
@access_permission(level = 10)
def index():
    announcements = Announcement.query.all()
    menu = Menu.query.all()
    videos = db.session.query(Video)
    return render_template("index.htm", title = 'Index', announcements = announcements, menu = menu, videos = videos, Video = Video)

@app.route("/listUser/")
@login_required
@access_permission(level = 5)
def listUser():
    announcements = Announcement.query.all()
    menu = Menu.query.all()
    users = User.query.filter(User.competence > current_user.competence)
    return render_template('listUser.htm', title = "List Users", users = users, announcements = announcements, menu = menu)

@app.route("/announcements/")
@login_required
@access_permission(level = 5)
def announcements():
    menu = Menu.query.all()
    announcements = db.session.query(Announcement).all()
    return render_template('announcements.htm', title = "Announcements", announcements = announcements, menu = menu)

@app.route('/video/')
def randomVideo(): # 隨機Video
    # with open('static/playlist.json', "r", encoding = 'utf8') as jsonFile:
    #     jsonData = json.load(jsonFile)
    videos = db.session.query(Video).all()
    return video(random.randrange(len(videos)))

@app.route('/video/<int:videoNum>')
@login_required
@access_permission(level = 10)
def video(videoNum):
    menu = Menu.query.all()
    videos = db.session.query(Video)
    announcements = Announcement.query.all()
    return render_template('video.htm', videoNum = videoNum, videos = videos, announcements = announcements, menu = menu)

@app.route('/api/')
def test():
    return jsonify(video = Video.collection, menu = Menu.collection, announcement = Announcement.collection)

@app.route('/list/')
def listRoot():
    return list("")
@app.route('/list/<string:path>/')
@login_required
@access_permission(level = 5)
def list(path):
    def formattime(time):
        return datetime.strftime(
            datetime.fromtimestamp(time),
            '%Y-%m-%d %H:%M:%S'
        )
    files = []
    folderpath = os.path.join(app.config['VIDEO_FOLDER'] , path)
    path = "/" + path
    for index, file in enumerate(os.listdir(folderpath)):
        filepath = os.path.join(folderpath, file)
        relativepath = os.path.join(path, file)
        files.append({
            "index": index,
            "name": file,
            "url": ("/view" if (os.path.isfile(filepath)) else "/list") + relativepath,
            "download_url": "/media" + relativepath,
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

@app.route('/view/<path:path>') # 強制檢視影片，而不是看瀏覽器而下載或觀看
@login_required
def view(path):
    announcements = Announcement.query.all()
    menu = Menu.query.all()
    absolutePath = re.match(r"^http(s|)://[^/:]{1,}", request.url).group(0)
    return render_template('viewMedia.htm', mediaFile = absolutePath + ":" + str(app.config['NGINX_PORT']) + "/" + path)

@app.route('/signup/')
def signup():
    form = SignupForm(request.form)
    return render_template('signup.htm', title = "Sign Up", form = form)

@app.route('/login/', methods = ['GET','POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():
    # if request.method == 'POST':
        user = User.getByAccount(form.account.data)
        if user:
            if (user.verify_password(form.password.data)):
                user.authenticated = True
                user.login_time = datetime.utcnow()
                user.login_ip = request.remote_addr
                db.session.add(user)
                db.session.commit()
                login_user(user, remember = True)
                next = request.args.get('next')
                flash('Logged in successfully.')
                return redirect(next or url_for("index"))
    return render_template('login.htm', title = "Login", form = form)

@app.route('/logout/', methods = ['POST'])
@login_required
def logout():
    logout_user()
    next = request.args.get('next')
    return redirect(next or url_for("index"))

@app.route('/upload/', methods = ['GET','POST']) # 上傳檔案
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
                file.save(os.path.join(app.config['VIDEO_FOLDER'], filename))
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
    return '.' in filename and filename.rsplit('.', 1)[-1] in app.config['ALLOWED_EXTENSIONS']
def filename_filter(filename):
    # filename = re.sub('[" "\/\--]+', '-', filename)
    # filename = re.sub(r':-', ':', filename)
    # filename = re.sub(r'^-|-$', '', filename)
    return filename

@app.route("/media/<path:path>") # 轉址到nginx伺服器
def media(path):
    mediaFileUrl = re.sub(r"(:[0-9]{0,}|)/media/", ":" + str(app.config['NGINX_PORT']) + "/", request.url) # nginx port
    return redirect(mediaFileUrl, code = 302)

@socketio.on('connect', namespace = '/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})

@socketio.on('watchTV', namespace = '/test')
def test_message(message):
    print(message['data'])
    emit('redirect', {'data': message['data'], 'count': 2, "url": "/video/32"})

def main():
    print("----------- Main -----------")
    if not os.environ.get('WERKZEUG_RUN_MAIN'):
        nginxRunning = b'nginx' in subprocess.Popen(
            'tasklist',
            stdout = subprocess.PIPE
        ).communicate()[0]
        if (not nginxRunning):
            print("Start nginx service!!")
            os.chdir(app.config['NGINX_FOLDER'])
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
    socketio.run(app, host = os.getenv('IP', "0.0.0.0"), port = int(os.getenv('PORT', 80)))
    # app.run(host = os.getenv('IP', "0.0.0.0"), port = int(os.getenv('PORT', 80)), threaded = True) #processes=1~9999
    if os.environ.get('WERKZEUG_RUN_MAIN'):
        os.system("taskkill /f /im nginx.exe");
    print("----------- End Main -----------")

if __name__ == '__main__':
    main()