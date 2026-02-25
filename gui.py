import bottle
import json
import os
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
    return user

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

@bottle.get('/music/<file:path>')
def static_music(file):
    return bottle.static_file(file, root='music')

@bottle.get('/temp/<file:path>')
def static_temp(file):
    return bottle.static_file(file, root='temp')

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
def song_search():
    query = bottle.request.query.query
    if query:
        results = Song.search(query)
    else:
        results = None
    return dict(query=query, results=results)

@bottle.get('/izvajalci/')
@bottle.view('usersearch.html')
def user_search():
    query = bottle.request.query.query
    if query:
        results = User.search(query)
    else:
        results = None
    return dict(query=query, results=results)

@bottle.get('/izdaje/')
@bottle.view('releasesearch.html')
def release_search():
    query = bottle.request.query.query
    if query:
        results = Release.search(query, "album")
        results.extend(Release.search(query, "single"))
        results.extend(Release.search(query, "ep"))
    else:
        results = None
    return dict(query=query, results=results)

@bottle.get('/izdaje/<id:int>/')
@bottle.view('release.html')
def release_songs(id):
    release = Release(id)
    songs = release.songs
    return dict(release=release, songs=songs)

@bottle.get('/uporabniki/<id:int>/')
@bottle.view('user.html')
def user_info(id):
    user = User(id)
    releases = user.releases
    return dict(releases=releases, _user=user)

@bottle.get('/nalaganje/')
@bottle.view('makerelease.html')
def make_release_get():
    if not logged_in_user():
        bottle.redirect('/prijava/')
    pass

@bottle.post('/nalaganje/')
def make_release_post():
    _user=logged_in_user()
    type=bottle.request.forms.type
    title=bottle.request.forms.title
    r_id=Release.new_release(_user.id, title, type, "./music/")
    bottle.redirect(f'/nalaganje/{r_id}/')

@bottle.get('/nalaganje/<r_id:int>/')
@bottle.view('upload.html')
def upload_get(r_id):
    return dict(r_id=r_id)

@bottle.post('/nalaganje/<r_id:int>/')
def upload_post(r_id):
    _user=logged_in_user()
    release=Release(r_id)
    # if release.author != _user.id:
        # set_message("Samo avtor izdaje lahko ji dodaja pesmi.")
        # bottle.redirect('/')
    file = bottle.request.files.get('upload')
    _, ext = os.path.splitext(file.filename)
    if ext != ".mp3":
        set_message("Dovoljeno je nalaganje samo mp3 datotek.")
        bottle.redirect(f'/nalaganje/{r_id}/')
    title=bottle.request.forms.title
    destination=os.path.join("/music/", str(r_id))
    order_num=len(os.listdir(destination))
    path=os.path.join("/temp/", str(order_num - 1))
    file.save(path)
    Song.new_song(r_id, order_num, title, path, destination)




bottle.BaseTemplate.defaults["read_message"] = read_message
bottle.BaseTemplate.defaults["read_form"] = read_form
bottle.BaseTemplate.defaults["logged_in_user"] = logged_in_user

if __name__ == '__main__':
    bottle.run(debug=True, reloader=True)