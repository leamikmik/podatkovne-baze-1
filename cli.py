import os, getpass, time
from enum import Enum
import model

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




def login():
    global loggedUser
    user = input("Username: ")
    password = getpass.getpass()
    try:
        loggedUser = model.User.login(user, password)
    except model.AuthError:
        print("Incorrect username/password")

def logout():
    global loggedUser
    loggedUser = None
    

def close():
    print("Goodbye!")

class HomeMenu(Menu):

    SEARCH = ("Search", lambda: switchToMenu(SearchMenu))
    #ADD = ("Add an entry (must be logged in)", function)
    LOGIN = ("Login", login)
    LOGOUT = ("Logout", logout)
    EXIT = ("Close the program", close)




searchTypes = ["Songs", "EP", "Album"]
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
            case _:
                raise ValueError(f'Incorrect object type {type(val)}')
        ret.append(SearchResultItem(text, fun))
    return ret

def searchGo():
    global currentMenu, results

    type = None
    match SearchMenu.TYPE.append:
        case "Songs":
            type = "songs"
            res = model.Song.search(SearchMenu.QUERY.append)
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
    if n == 0:
        page = 1
    elif page > (len(results)+10)//10 or page < 1:
        page -= n
        return
    SearchResultsMenu.PREV.append = f"\n---------- {page}/{(len(results)+10)//10} ----------"

def showSong(song):
    global currentMenu
    if not isinstance(song, model.Song):
        song = model.Song(song)
    release = model.Release(song.release)
    print(
f"""{song}
- Author: {song.author}
- Release: {release}
- Released on: {time.ctime(release.date)}
- Length: {model.seconds_to_str(song.length)}
- File location: {song.location}"""
    )
    SongInfoMenu.RELEASE.fun = refresh(lambda: showRelease(release))
    currentMenu = SongInfoMenu

def showRelease(release):
    global currentMenu
    if not isinstance(release, model.Release):
        release = model.Release(release)
    print(
f"""{release}
- Author: {release.author}
- Type: {release.type.capitalize()}
- Released on: {time.ctime(release.date)}
- Length: {model.seconds_to_str(release.length)}
- Number of songs: {len(release.songs)}
- Release location: {release.location}"""
    )
    ReleaseInfoMenu.SONGS.fun = refresh(lambda: showReleaseSongs(release.songs))
    currentMenu = ReleaseInfoMenu

def showReleaseSongs(songs):
    global results, currentMenu
    results = resToMenu(songs)
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
    RELEASE = ("See release", None)

class ReleaseInfoMenu(Menu):
    BACK = ("Back", lambda: switchToMenu(SearchResultsMenu))
    SONGS = ("Show songs", None)


currentMenu = HomeMenu # Trenutno izbran meni
loggedUser = None

def selectMenu(menu):
    startNum = 1

    if menu == HomeMenu:
        menu = list(menu)
        if loggedUser:
            menu.pop(-3)
        else:
            menu.pop(-2)
    elif menu == SearchResultsMenu:
        menu = list(menu) + results[10*(page-1):min(10*page, len(results))]
    else:
        menu = list(menu)
    print("\nSelect an option:")
    for i, val in enumerate(menu, startNum):
        print(f"({i}) {val}")

    while True:
        try: 
            inp = int(input("> ")) - 1
            return menu[inp]
        except (IndexError, ValueError):
            print("Incorrect selection!")

@refresh
def run():
    while True:
        if currentMenu:
            selection = selectMenu(currentMenu)
            selection.fun()
        if selection == HomeMenu.EXIT:
            return

if __name__ == "__main__":
    run()