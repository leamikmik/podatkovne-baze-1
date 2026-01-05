import os, getpass
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



def backToHome():
    global currentMenu
    currentMenu = HomeMenu

def toSearch():
    global currentMenu
    currentMenu = SearchMenu

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

    SEARCH = ("Search", toSearch)
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
    global currentMenu
    currentMenu = None

    type = None
    match SearchMenu.TYPE.append:
        case "Songs":
            results = model.Song.search(SearchMenu.QUERY.append)
        case _:
            type = SearchMenu.TYPE.append.lower()
            results = model.Release.search(SearchMenu.QUERY.append, type)
    resLen = len(results)
    page = 1
    print("""(1) Back
(2) Next page
(3) Previous page
""")
    for i, val in enumerate(results, 1):
        if i > page*10:
            break
        print(f"({i+3}) {val.title} - {val.author}")

class SearchMenu(Menu):
    BACK = ("Back", backToHome)
    TYPE = ("What to search for: ", typeSwap)
    QUERY = ("Query: ", searchQuery)
    SEARCH = ("Go", searchGo)

SearchMenu.TYPE.append = searchTypes[0]




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