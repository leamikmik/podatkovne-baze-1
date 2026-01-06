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

def searchGo():
    global currentMenu, page, results

    type = None
    match SearchMenu.TYPE.append:
        case "Songs":
            type = "songs"
            res = model.Song.search(SearchMenu.QUERY.append)
        case _:
            type = SearchMenu.TYPE.append.lower()
            res = model.Release.search(SearchMenu.QUERY.append, type)

    results = []
    page = 1
    for val in res:
        results.append(SearchResultItem(f"{val.title} - {val.author}", lambda x=val.id: showSong(x)))
    currentMenu = SearchResultsMenu
    SearchResultsMenu.PREV.append = f"\n---------- {page}/{(len(results)+10)//10} ----------"

class SearchMenu(Menu):
    BACK = ("Back", lambda: switchToMenu(HomeMenu))
    TYPE = ("What to search for: ", typeSwap)
    QUERY = ("Query: ", searchQuery)
    SEARCH = ("Go", searchGo)
SearchMenu.TYPE.append = searchTypes[0]



def changePage(n):
    global page
    page += n
    if page > (len(results)+10)//10 or page < 1:
        page -= n
        return
    SearchResultsMenu.PREV.append = f"\n---------- {page}/{(len(results)+10)//10} ----------"

def showSong(id):
    global currentMenu
    song = model.Song(id)
    release = model.Release(song.release)
    print(f"{song}")
    print(f"- Author: {song.author}")
    print(f"- Release: {release}")
    print(f"- Released on: {time.ctime(release.date)}")
    print(f"- Length: {model.seconds_to_str(song.length)}")
    print(f"- File location: {song.location}")
    currentMenu = SongMenu

def showRelease(id, showSongs=False):
    global currentMenu
    release = model.Release(id)
    pass

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

class SongMenu(Menu):
    BACK = ("Back", lambda: switchToMenu(SearchResultsMenu))
    RELEASE = ("See release", lambda: switchToMenu(SearchResultsMenu))



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