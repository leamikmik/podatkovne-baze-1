import os
from getpass import getpass
from subprocess import Popen, DEVNULL
from time import ctime
from enum import Enum
import model

def _ni():
    print("Not implemented :(")

def refresh(f):
    """
    Izbriše tekst v konzoli.
    
    :param f: function
    """
    def wrap(*args, **kwargs):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            f(*args, **kwargs)
        except KeyboardInterrupt:
            print()
    return wrap

def switchToMenu(menu):
    global currentMenu
    currentMenu = menu

class Menu(Enum):
    """
    Razred za izbiro
    """
    def __init__(self, title, f, append=""):
        self.title = title
        self.fun = refresh(f)
        self.append = append
    
    def __str__(self):
        return self.title + self.append


def register():
    global loggedUser
    print("Registering")
    user = input("Username: ")
    password = getpass()
    password2 = getpass(prompt="Re-enter password:")
    if password != password2:
        print("Passwords not the same!")
        return
    try:
        user = model.User.register(user, password)
        loggedUser = user
        HomeMenu.MYPROF.fun = refresh(lambda: showUser(loggedUser, loggedUserMenu))
        manageReleasesMenu.BACK.fun = HomeMenu.MYPROF.fun
    except model.AuthError:
        print("Username already taken!")
    

def login():
    global loggedUser
    print("Logging in")
    user = input("Username: ")
    password = getpass()
    try:
        loggedUser = model.User.login(user, password)
        HomeMenu.MYPROF.fun = refresh(lambda: showUser(loggedUser, loggedUserMenu))
        manageReleasesMenu.BACK.fun = HomeMenu.MYPROF.fun
    except model.AuthError:
        print("Incorrect username/password")

def logout():
    global loggedUser
    loggedUser = None
    

def close():
    print("Goodbye!")

class HomeMenu(Menu):

    SEARCH = ("Search", lambda: switchToMenu(SearchMenu))
    MYPROF = ("My profile", None)
    LOGIN = ("Login", login)
    REGISTER = ("Register", register)
    LOGOUT = ("Logout", logout)
    EXIT = ("Close the program", close)




searchTypes = ["Song", "EP", "Album", "User"]
def typeSwap():
    searchTypes.append(searchTypes.pop(0))
    SearchMenu.TYPE.append = searchTypes[0]

def searchQuery():
    inp = input("Query: ")
    SearchMenu.QUERY.append = inp

def resToMenu(res):
    ret = []
    for val in res:
        match val:
            case model.Song():
                text = f"{val} by {val.author} - {model.seconds_to_str(val.length)}"
                fun = lambda x=val: showSong(x)
            case model.Release():
                text = f"{val} by {val.author}"
                fun = lambda x=val: showRelease(x) 
            case model.User():
                text = val.name
                fun = lambda x=val: showUser(x, UserInfoMenu)
            case _:
                raise ValueError(f'Incorrect object type {type(val)}')
        ret.append(SearchResultItem(text, fun))
    return ret

def searchGo():
    global currentMenu, results

    match SearchMenu.TYPE.append:
        case "Song":
            res = model.Song.search(SearchMenu.QUERY.append)
        case "User":
            res = model.User.search(SearchMenu.QUERY.append)
        case _:
            type = SearchMenu.TYPE.append.lower()
            res = model.Release.search(SearchMenu.QUERY.append, type)

    results = resToMenu(res)
    changePage(0)
    currentMenu = SearchResultsMenu

class SearchMenu(Menu):
    BACK = ("Back", lambda: switchToMenu(HomeMenu))
    TYPE = ("What to search for: ", typeSwap)
    QUERY = ("Query: ", searchQuery)
    SEARCH = ("Go", searchGo)
SearchMenu.TYPE.append = searchTypes[0]



def changePage(n):
    global page
    page += n
    maxPages = (len(results)+9)//10
    if n == 0:
        page = 1
    elif page > maxPages or page < 1:
        page -= n
        return
    SearchResultsMenu.PREV.append = f"\n---------- {page if maxPages > 0 else 0}/{maxPages} ----------"

def playSong(song):
    if not isinstance(song, model.Song):
        song = model.Song(song)
    Popen(["vlc",  song.location], stdout=DEVNULL, stderr=DEVNULL)

def showSong(song):
    global currentMenu
    if not isinstance(song, model.Song):
        song = model.Song(song)
    release = model.Release(song.release)
    print(
f"""{song}
- Author: {song.author}
- Release: {release}
- Released on: {ctime(release.date)}
- Length: {model.seconds_to_str(song.length)}
- File location: {song.location}"""
    )
    SongInfoMenu.RELEASE.fun = refresh(lambda: showRelease(release))
    SongInfoMenu.PLAY.fun = refresh(lambda: playSong(song))
    currentMenu = SongInfoMenu

def showRelease(release):
    global currentMenu
    if not isinstance(release, model.Release):
        release = model.Release(release)
    print(
f"""{release}
- Author: {release.author}
- Type: {release.type.capitalize()}
- Released on: {ctime(release.date)}
- Length: {model.seconds_to_str(release.length)}
- Number of songs: {len(release.songs)}
- Release location: {release.location}"""
    )
    ReleaseInfoMenu.SONGS.fun = refresh(lambda: showEntries(release.songs))
    currentMenu = ReleaseInfoMenu

def showUser(user, menu):
    global currentMenu
    if not isinstance(user, model.User):
        user = model.User(user)
    songs = []
    for rel in user.releases:
        songs += rel.songs
    
    print(
f"""{user}
- Joined on: {ctime(user.date)}
- Number of releases: {len(user.releases)}
- Number of songs: {len(songs)}"""
    )
    menu.ALBUM.fun = refresh(lambda: showEntries(user.getReleases("album")))
    menu.EP.fun = refresh(lambda: showEntries(user.getReleases("ep")))
    menu.SINGLE.fun = refresh(lambda: showEntries(user.getReleases("single")))
    menu.SONG.fun = refresh(lambda: showEntries(songs))
    currentMenu = menu

def showEntries(res):
    global results, currentMenu
    results = resToMenu(res)
    changePage(0)
    currentMenu = SearchResultsMenu

page, results = 1, []
class SearchResultsMenu(Menu):
    BACK = ("Back", lambda: switchToMenu(SearchMenu))
    NEXT = ("Next page", lambda: changePage(1))
    PREV = ("Previous page", lambda: changePage(-1))

class SearchResultItem:
    def __init__(self, name, f):
        self.name = name
        self.fun = refresh(f)

    def __str__(self):
        return self.name

class SongInfoMenu(Menu):
    BACK = ("Back", lambda: switchToMenu(SearchResultsMenu))
    PLAY = ("Play the song in VLC", None)
    RELEASE = ("See release", None)

class ReleaseInfoMenu(Menu):
    BACK = ("Back", lambda: switchToMenu(SearchResultsMenu))
    SONGS = ("Show songs", None)

class UserInfoMenu(Menu):
    BACK = ("Back", lambda: switchToMenu(SearchResultsMenu))
    ALBUM = ("See albums", None)
    EP = ("See EPs", None)
    SINGLE = ("See singles", None)
    SONG = ("See all songs", None)


addingRelease = {"title": None, "type": ["Single", "Album", "EP"], "songs": []}



class loggedUserMenu(Menu):
    BACK = ("Back", lambda: switchToMenu(HomeMenu))
    ALBUM = ("See albums", None)
    EP = ("See EPs", None)
    SINGLE = ("See singles", None)
    SONG = ("See all songs", None)
    MANAGE = ("Manage releases", lambda: switchToMenu(manageReleasesMenu))

class manageReleasesMenu(Menu):
    BACK = ("Back", None)
    ADDREL = ("Add release", None)
    EDITREL = ("Edit release", None)
    EDITSONG = ("Edit song", None)

class addReleaseMenu(Menu):
    BACK = ("Back", lambda: currentMenu(manageReleasesMenu))
    TITLE = ("Title: ", None)
    TYPE = {"Type: ", None}
    SONGS = {"Songs: ", None, "0"}
    ADD = {"Complete", None}
addReleaseMenu.TYPE.append = addingRelease["type"][0]

currentMenu = HomeMenu # Trenutno izbran meni
loggedUser = None

def selectMenu(menu):
    startNum = 1

    if menu == HomeMenu:
        menu = list(menu)
        if loggedUser:
            menu.pop(-3)
            menu.pop(-3)
        else:
            menu.pop(1)
            menu.pop(-2)
    elif menu == SearchResultsMenu:
        menu = list(menu) + results[10*(page-1):min(10*page, len(results))]
    elif menu == SongInfoMenu:
        menu = list(menu)
        if not vlc:
            menu.pop(1)
    else:
        menu = list(menu)
    print("\nSelect an option:")
    for i, val in enumerate(menu, startNum):
        print(f"[{i}] {val}")

    while True:
        try: 
            inp = int(input("> ")) - 1
            return menu[inp]
        except (IndexError, ValueError):
            print("Incorrect selection!")
vlc = False
@refresh
def run():
    global vlc
    vlc = os.system("vlc --version > /dev/null 2>&1") == 0
    while True:
        if currentMenu:
            selection = selectMenu(currentMenu)
            if selection.fun:
                selection.fun()
            else:
                _ni()
        if selection == HomeMenu.EXIT:
            return

if __name__ == "__main__":
    run()