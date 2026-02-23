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

def set_message(message):
    set_cookie("msg", message)

def read_message():
    message=get_cookie('msg')
    del_cookie('msg')
    return message

def set_form(cookie, form):
    set_cookie(cookie, json.dumps(form))

def read_form(cookie, default={}, delete=True):
    try:
        return json.loads(get_cookie(cookie, delete))
    except (TypeError, json.JSONDecodeError):
        return default

def logged_in_user():
    uid=bottle.request.get_cookie('user', secret=SECRET)
    try:
        user = User(uid)
    except:
        return False
    return str(user)

def login_user(user, cookie="None"):
    if not user:
        set_message("user not found")
        bottle.redirect("/prijava/")
    bottle.response.set_cookie('user', user.id, secret=SECRET, path="/")
    if cookie:
        del_cookie(cookie)
    bottle.redirect("/")

def logout_user():
    del_cookie('user')
    bottle.redirect('/')

@bottle.get('/static/<file:path>')
def static(file):
    return bottle.static_file(file, root='static')

@bottle.get('/')
@bottle.view('index.html')
def index():
    pass

@bottle.get('/prijava/')
@bottle.view('login.html')
def login():
    pass

@bottle.post('/prijava/')
def login_post():
    username=bottle.request.forms.username
    password=bottle.request.forms.password
    set_form('login', {'username':username})
    try:
        user = User.login(username, password)
    except:
        set_message("user not found")
        bottle.redirect("/prijava/")
    login_user(user, cookie='login')

@bottle.get('/registracija/')
@bottle.view('registration.html')
def register():
    pass

@bottle.post('/registracija/')
def register_post():
    username=bottle.request.forms.username
    password1=bottle.request.forms.password1
    password2=bottle.request.forms.password2
    set_form('register', {'username': username})
    if password1 is not password2:
        set_message('passwords dont match')
        bottle.redirect('/registracija/')
    user=User.register(username, password1)
    login_user(User.login(username, password1), cookie='login')

@bottle.get('/odjava/')
def odjava():
    logout_user()

@bottle.get('/pesmi/')
@bottle.view('songsearch.html')
def song_search_post():
    query = bottle.request.query.query
    if query:
        results = Song.search(query)
    else:
        results = None
    return dict(query=query, results=results)

bottle.BaseTemplate.defaults["read_message"] = read_message
bottle.BaseTemplate.defaults["read_form"] = read_form
bottle.BaseTemplate.defaults["logged_in_user"] = logged_in_user

if __name__ == '__main__':
    bottle.run(debug=True, reloader=True)