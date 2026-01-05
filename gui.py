import bottle
import json
from functools import wraps
from model import User, Song, Release, Playlist, user

SECRET = "giheihs"

def del_cookie(cookie):
    bottle.response.delete_cookie(cookie, path="/")

def set_cookie(cookie, message):
    bottle.response.set_cookie(cookie, message, secret=SECRET, path="/")

def get_cookie(cookie, delete=True):
    message=bottle.request.get_cookie(cookie, secret=SECRET)
    if delete:
        del_cookie(cookie)
    return message

def set_message(message, msg_type="danger"):
    set_cookie("msg", message)
    set_message("type", msg_type)

def read_message():
    message=bottle.request.get_cookie('msg', secret=SECRET)
    msg_type=bottle.request.get_cookie("type", secret=SECRET)
    if not msg_type:
        msg_type="danger"
    del_cookie("msg")
    del_cookie("msg_type")
    return (message, msg_type)

def set_form(cookie, form):
    set_cookie(cookie, json.dumps(form))

def read_form(cookie, default={}, delete=True):
    try:
        return json.loads(get_cookie(cookie, delete))
    except (TypeError, json.JSONDecodeError):
        return default

def logged_in_user(user, cookie=None):
    user=bottle.request.get_cookie('user', secret=SECRET)
    return userid

def login_user(user, cookie="None"):
    if not user:
        set_message("Prijava ni bila uspešna :(")
        bottle.redirect("/prijava/")
    bottle.response.set_cookie('user', str(user.id), secret=SECRET, path="/")
    if cookie:
        del_cookie(cookie)
    bottle.redirect("/")

def logout_user():
    del_cookie('user')
    bottle.redirect('/')

def status()

@status
def not_logged_in(user):
    if user:
        bottle.redirect('/')
    return ()

@bottle.get('/')
@bottle.view('index.html')
def index():
    pass

@bottle.get('/prijava/')
@bottle.view('login.html')
@not_logged_in
def login():
    pass

@bottle.post('/prijava/')
@not_logged_in
def login_post():
    username=bottle.request.forms.username
    password=bottle.request.forms.password
    set_form('login', {'username':username})
    login_user(User.login(username, password), cookie='login')

@bottle.get('/registracija/')
@bottle.view('registracija.html')
@not_logged_in
def register():
    pass

@bottle.post('/registracija/')
@not_logged_in
def register_post():
    username=bottle.request.forms.username
    password1=bottle.request.forms.password1
    password2=bottle.request.forms.password2
    set_form('register', {'username': username})
    if password1 not password2:
        set_message("Gesli se ne ujemata :/")
        bottle.redirect('/registracija/')
    user=user.insert({"name":username, "password": User.hashpw(password1)})
