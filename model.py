import sqlite3, bcrypt, db, os

conn = sqlite3.connect('music.db')
cur = conn.cursor()

user, release, song, playlist, phs = db.setup_db(conn)

def seconds_to_str(seconds):
    """
    Prevede sekunde v h:m:s
    """
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return '%d:%02d:%02d' % (hour, min, sec) if hour > 0 else '%02d:%02d' % (min, sec)

class AuthError(Exception):
    # Napaka pri autentikaciji
    pass

class User:
    '''
    Razred za uporabnika
    '''

    def __init__(self, id, name=None, date=None):
        if id and not name and not date:
            q = "SELECT name, date_created FROM User WHERE id = ?"
            res = conn.execute(q, [id]).fetchone()
            if res is None:
                raise ValueError("User not found")
            name, date = res
        
        self.id = id
        self.name = name
        self.date = date

    def __str__(self):
        return self.name
    
    @staticmethod
    # Vrne vpisanega uporabnika, če pravilno vnešeni podatki
    def login(name, inp_passw):
        q = "SELECT id, password, date FROM User WHERE ime = ?;"
        res = conn.execute(q, [name]).fetchone()
        if res is None:
            raise AuthError("User not found")
        id, password, date = res
        if bcrypt.checkpw(inp_passw.encode('utf-8'), password.encode('utf-8')):
            return User(id, name, date)
        else:
            raise AuthError("Incorrect password")
        
    @staticmethod
    # Vrne niz hashed gesla
    def hashpw(passw):
        return bcrypt.hashpw(passw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
    @staticmethod
    # Poišče uporabnike z podnizom v imenu 
    def search(query):
        q = "SELECT id, name, date_created FROM User WHERE name LIKE ?"
        for id, name, date in conn.execute(q, [f"%{query}%"]):
            yield User(id, name, date)

class Song:
    '''
    Razred za pesem
    '''

    def __init__(self, id, release, order_num, title, length):
        self.id = id
        self.order = order_num
        self.release = release
        self.title = title
        self.length = length # V sekundah
        self.location = os.path.join(".", "music",str(release),f"{order_num}.mp3")

    def __str__(self):
        return self.title


class Release:
    '''
    Razred za izdajo
    '''

    def __init__(self, id, author, title, type, date):
        self.author = author
        self.title = title
        self.type = type
        self.date = date
        self.id = id
        self.songs = []
        self._length = None

    def __str__(self):
        return self.title
    
    # Napolni seznam pesmi v izdaji z objekti
    def populate(self):
        q = "SELECT id, order_num, title, length FROM Song WHERE release = ? ORDER BY order_num ASC"
        if not self.songs:
            for id, order_num, title, length in conn.execute(q, [self.id]):
                self.songs.append(Song(id, self.id, order_num, title, length))

    @property
    def length(self):
        if not self.songs:
            self.populate()
        if self._length is None:
            length = 0
            for song in self.songs:
                length += song.length
            self._length = length
        return self._length

    @staticmethod
    # Poišče izdaje z podnizom
    def search(query):
        q = "SELECT id, author, title, type, date_released FROM Release WHERE title LIKE ?"
        for id, author, title, type, date in conn.execute(q, [f"%{query}%"]):
            yield Release(id, author, title, type, date)

class Playlist:
    '''
    Razred za seznam pesmi
    '''

    def __init__(self, id, owner, name, date):
        self.owner = User(id=owner)
        self.date = date
        self.name = name
        self.id = id
        self.songs = []
        self._length = None

    def __str__(self):
        return self.name

    @property
    def length(self):
        if not self.songs:
            self.populate()
        if self._length is None:
            length = 0
            for song in self.songs:
                length += song.length
            self._length = length
        return self._length

    # Napolni seznam pesmi z objekti
    def populate(self):
        q = "SELECT id, release, order_num, title, length FROM Song s JOIN RIGHT Playlist_Has_Song ps ON s.id = ps.song_id WHERE playlist_id = ? ORDER BY order_num ASC"
        if not self.songs:
            for id, release, order_num, title, length in conn.execute(q, [self.id]):
                self.songs.append(Song(id, release, order_num, title, length))
