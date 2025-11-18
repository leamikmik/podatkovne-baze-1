import sqlite3, bcrypt, db
# Check if password correct

conn = sqlite3.connect('music.db')
cur = conn.cursor()

user, release, song, playlist, phs = db.setup_db(conn)

class AuthError(Exception):
    # Napaka pri autentikaciji
    pass

class User:
    '''
    Razred za uporabnika
    '''

    # Konstruktor
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

    # Izpis uporabnika
    def __str__(self):
        return self.ime
    
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
    def search(query):
        q = "SELECT id, name, date_created FROM User WHERE name LIKE ?"
        for id, name, date in conn.execute(q, [f"%{query}%"]):
            yield User(id, name, date)

class Song:
    '''
    Razred za pesem
    '''

    def __init__(self, id, title, release, f_location):
        self.id = id
        self.title = title
        self.release = release
        self.location = f_location

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

    def __str__(self):
        return self.title
    
    def populate(self):
        q = "SELECT id, title, file_location FROM Song WHERE release = ? ORDER BY order_num ASC"
        if not self.songs:
            for id, title, f_location in conn.execute(q, [self.id]):
                self.songs.append(Song(id, title, self.id, f_location))

    @staticmethod
    def search(query):
        q = "SELECT id, author, title, type, date_release FROM Release WHERE title LIKE ?"
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

    def __str__(self):
        return self.name
    
    def populate(self):
        q = "SELECT id, title, release, file_location FROM Song s JOIN RIGHT Playlist_Has_Song ps ON s.id = ps.song_id WHERE playlist_id = ? ORDER BY order_num ASC"
        if not self.songs:
            for id, title, release, f_location in conn.execute(q, [self.id]):
                self.songs.append(Song(id, title, release, f_location))