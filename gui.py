import bottle
import json
from functools import wraps
from model import User, Song, Release, Playlist

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
    message=bottle.request.get_cookie("msg", secret=SECRET)
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
    idu=bottle.request.get_cookie("user", secret=SECRET)
    return User.

def log_in_user(user, cookie="None"):
    if not user:
        set_message("Prijava ni bila uspešna :(")
        bottle.redirect("/prijava/")
    bottle.response.set_cookie("user", str(user.id), secret=SECRET, path="/")
    if cookie:
        del_cookie(cookie)
    bottle.redirect("/")



