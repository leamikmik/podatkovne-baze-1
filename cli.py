import os
from getpass import getpass
from subprocess import Popen, DEVNULL
from time import ctime
from enum import Enum
import model

#
# Program za iskanje in ogled glasbe v bazi
#


#############################
# Osnovne metode in razredi #
#############################

def refresh(f):
    """
    Izbriše tekst v konzoli.
    
    :param f: function
    """
    def wrap(*args, **kwargs):
        try:
            os.system('cls' if os.name == 'nt' else 'clear') # Izbriše trenutni izpis v konzoli, odvisno od OS
            f(*args, **kwargs)
        except KeyboardInterrupt:
            print()
    return wrap

def switchToMenu(menu):
    """
    Spremeni trenutni meni na podanega.
    
    :param menu: Objekt tipa meni, na katerega nastavimo trenutni meni
    """
    global currentMenu
    currentMenu = menu

def selectMenu(menu):
    """
    Izpiše izbire trenutnega menija, in vrne izbrano
    
    :param menu: Meni katerega izpišemo
    """
    # Spremeni možne izbire glede na meni
    if menu == HomeMenu: 
        menu = list(menu)
        if loggedUser: # Izbriše možnosti za vpis
            menu.pop(-3)
            menu.pop(-3)
        else: # Izbriše možnosti za izpis in ogled uporabnika
            menu.pop(1)
            menu.pop(-2)

    elif menu == SearchResultsMenu:
        menu = list(menu) + results[10*(page-1):min(10*page, len(results))] # Doda rezultate iskanja

    elif menu == SongInfoMenu:
        menu = list(menu)
        if not vlc: # Izbriše možnost igranja pesmi
            menu.pop(1)

    else:
        menu = list(menu)

    print("\nSelect an option:")
    for i, val in enumerate(menu, 1):
        print(f"[{i}] {val}")

    while True: # Čakamo na pravilen vnos izbire
        try: 
            inp = int(input("> ")) - 1
            return menu[inp]
        except (IndexError, ValueError):
            print("Incorrect selection!")

class Menu(Enum):
    """
    Razred za izbiro.

    :param title: Naslov izbire
    :param f: Funkcija ki se izvede ob izbiri, ovita v metodo refresh
    :param append: Tekst, ki je dodan na koncu izpisa. Privzeto je prazen
    """
    def __init__(self, title, f, append=""):
        self.title = title
        self.fun = refresh(f)
        self.append = append
    
    def __str__(self):
        return self.title + self.append

def close():
    """
    Izpis, ko uporabnik zapre program.

    """
    print("Goodbye!")


#######################################
# Metode za upravljanje z uporabnikom #
#######################################

def register():
    """
    Vpiše novega uporabnika v bazo.

    """
    global loggedUser
    print("Registering")
    user = input("Username: ")
    password = getpass()
    password2 = getpass(prompt="Re-enter password:")

    if password != password2:
        print("Passwords not the same!")
        return
    
    try: # Poskusi vnesti uporabnika, če le ta ne obstaja
        user = model.User.register(user, password)
        loggedUser = user
        HomeMenu.MYPROF.fun = refresh(lambda: showUser(loggedUser, loggedUserMenu)) 
    except model.AuthError:
        print("Username already taken!")
    

def login():
    """
    Prijavi že-obstoječega uporabnika

    """
    global loggedUser
    print("Logging in")
    user = input("Username: ")
    password = getpass()

    try:
        loggedUser = model.User.login(user, password)
        HomeMenu.MYPROF.fun = refresh(lambda: showUser(loggedUser, loggedUserMenu))
    except model.AuthError:
        print("Incorrect username/password")

def logout():
    """
    Izpiše uporabnika

    """
    global loggedUser
    loggedUser = None
    

#####################
# Metode za iskanje #
#####################

def typeSwap():
    """
    Zamenja izbiro tipa iskanja
    """
    searchTypes.append(searchTypes.pop(0))
    SearchMenu.TYPE.append = searchTypes[0]

def searchQuery():
    """
    Prebere poizvedbo iskanja
    """
    inp = input("Query: ")
    SearchMenu.QUERY.append = inp

def resToMenu(res):
    """
    Pretvori list objektov v vnose za meni.
    
    :param res: List rezultatov iskanja
    """
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
    """
    Zažene iskanje in spremeni meni 
    """
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

def changePage(n):
    """
    Zamenja stran rezultatov iskanja
    
    :param n: Zamik strani, oz. ponastavitev v primeru 0
    """
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
    """
    V novem oknu odpre pesem v VLC, če je ta naložen
    
    :param song: Pesem
    """
    if not isinstance(song, model.Song):
        song = model.Song(song)
    Popen(["vlc",  song.location], stdout=DEVNULL, stderr=DEVNULL)

def showEntries(res):
    """
    Izpiše podane podatke v obliki iskanja
    
    :param res: Podatki
    """
    global results, currentMenu
    results = resToMenu(res)
    changePage(0)
    currentMenu = SearchResultsMenu

class SearchResultItem:
    """
    Pomožni razred za lažjo obravnavo rezultatov iskanja

    :param title: Naslov izbire
    :param f: Funkcija ki se izvede ob izbiri, ovita v metodo refresh
    """
    def __init__(self, name, f):
        self.name = name
        self.fun = refresh(f)

    def __str__(self):
        return self.name
    

############################
# Metode za izpis podatkov #
############################

def showSong(song):
    """
    Izpiše podatke o pesmi
    
    :param song: Pesem
    """
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
    """
    Izpiše podatke o izdaji
    
    :param release: Izdaja
    """
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
    """
    Izpiše podatke o uporabniku
    
    :param user: Uporabnik
    :param menu: Meni ki ga nastavimo za trenutnega
    """
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


###################
# Razredi menijev #
###################

class HomeMenu(Menu):
    """
    Začetni meni
    """
    SEARCH = ("Search", lambda: switchToMenu(SearchMenu))
    MYPROF = ("My profile", None)
    LOGIN = ("Login", login)
    REGISTER = ("Register", register)
    LOGOUT = ("Logout", logout)
    EXIT = ("Close the program", close)

class SearchMenu(Menu):
    """
    Meni za vnos iskanja
    """
    BACK = ("Back", lambda: switchToMenu(HomeMenu))
    TYPE = ("What to search for: ", typeSwap, "Song")
    QUERY = ("Query: ", searchQuery)
    SEARCH = ("Go", searchGo)

class SearchResultsMenu(Menu):
    """
    Meni rezultatov iskanja
    """
    BACK = ("Back", lambda: switchToMenu(SearchMenu))
    NEXT = ("Next page", lambda: changePage(1))
    PREV = ("Previous page", lambda: changePage(-1))

class SongInfoMenu(Menu):
    """
    Meni za podatke o pesmi
    """
    BACK = ("Back", lambda: switchToMenu(SearchResultsMenu))
    PLAY = ("Play the song in VLC", None)
    RELEASE = ("See release", None)

class ReleaseInfoMenu(Menu):
    """
    Meni za podatke o izdaji
    """
    BACK = ("Back", lambda: switchToMenu(SearchResultsMenu))
    SONGS = ("Show songs", None)

class UserInfoMenu(Menu):
    """
    Meni za podatke o uporabniku
    """
    BACK = ("Back", lambda: switchToMenu(SearchResultsMenu))
    ALBUM = ("See albums", None)
    EP = ("See EPs", None)
    SINGLE = ("See singles", None)
    SONG = ("See all songs", None)

class loggedUserMenu(Menu):
    """
    Meni za podatke o prijavljenemu uporabniku
    """
    BACK = ("Back", lambda: switchToMenu(HomeMenu))
    ALBUM = ("See albums", None)
    EP = ("See EPs", None)
    SINGLE = ("See singles", None)
    SONG = ("See all songs", None)


#############################################################
# Začetek programa in inicializacije globalnih spremenljivk #
#############################################################

vlc = False # Ali ima uporabnik naložen VLC
currentMenu = HomeMenu # Trenutno izbran meni
page, results = 1, [] # Stran in rezultati iskanja
searchTypes = ["Song", "EP", "Album", "User"] # Možni tipi iskanja
loggedUser = None # Prijavljen uporabnik

@refresh
def run():
    """
    Glavni krog programa
    """
    global vlc
    vlc = os.system("vlc --version > /dev/null 2>&1") == 0 # Preveri ali ima uporabnik naložen VLC
    while True:
        if currentMenu:
            selection = selectMenu(currentMenu)
            if selection.fun is not None:
                selection.fun()
        if selection == HomeMenu.EXIT:
            return

if __name__ == "__main__":
    run()