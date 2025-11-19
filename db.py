import csv

class Table:
    """
    Osnova za razrede tabel
    """
    name = None # Ime v bazi
    location = None # Lokacija začetnih podatkov
    columns = {} # Dovoljena imena stolpcov

    def setup(self, q):
        """
        Ponastavi tabelo
        """
        self.drop()
        self.conn.execute(q)
        self.import_data()

    def __init__(self, conn):
        self.conn = conn

    def import_data(self):
        """
        Prebere in vnese začetne podatke
        """
        with open(self.location) as f:
            data = csv.reader(f)
            columns = next(data)
            for row in data:
                self.insert(**{k: None if v == "" else v for k, v in zip(columns, row)})

    def drop(self):
        """
        Izbriše tabelo
        """
        self.conn.execute(f"DROP TABLE IF EXISTS {self.name}")

    def insert(self, **values):
        """
        Vnese podane podatke v tabelo
        """
        if not set(values.keys()).issubset(self.columns):
            raise ValueError("Incorrect columns")
        
        q = f"INSERT INTO {self.name} ({",".join(values.keys())}) VALUES ({("?, "*len(values))[:-2]});"
        cur = self.conn.execute(q, list(values.values()))
        return cur.lastrowid
    
class User(Table):

    name = "User"
    location = "data/user.csv"
    columns = {"id", "name", "password", "date_created"}

    def setup(self):
        q = """
        CREATE TABLE User(
	        id INTEGER PRIMARY KEY,
	        name TEXT NOT NULL UNIQUE,
	        password TEXT NOT NULL,
	        date_created INTEGER NOT NULL DEFAULT (unixepoch('now'))
        );"""
        super().setup(q)
    
class Release(Table):

    name = "Release"
    location = "data/release.csv"
    columns = {"id", "author", "title", "type", "date_released"}

    def setup(self):
        q = """
        CREATE TABLE Release(
	        id INTEGER PRIMARY KEY,
	        author INTEGER NOT NULL,
	        title TEXT NOT NULL,
	        type TEXT NOT NULL CHECK ( type IN ("single", "ep", "album") ),
	        date_released INTEGER NOT NULL DEFAULT (unixepoch('now')),
	        FOREIGN KEY (author)
	        	REFERENCES User (id)
        );"""
        super().setup(q)

    def insert(self, **values):
        if values["type"] not in {"single", "ep", "album"}:
            raise ValueError("Incorrect release type")
        return super().insert(**values)

class Song(Table):
    
    name = "Song"
    location = "data/song.csv"
    columns = {"id", "release", "order_num", "title", "length"}

    def setup(self):
        q = """
        CREATE TABLE Song(
	        id INTEGER PRIMARY KEY,
	        release INTEGER NOT NULL,
	        order_num INTEGER NOT NULL,
	        title TEXT NOT NULL,
            length INTEGER NOT NULL,
	        FOREIGN KEY (release)
	        	REFERENCES Release (id)
        );"""
        super().setup(q)

class Playlist(Table):

    name = "Playlist"
    location = "data/playlist.csv"
    columns = {"id", "owner", "name", "date_created"}

    def setup(self):
        q = """
        CREATE TABLE Playlist(
	        id INTEGER PRIMARY KEY,
	        owner INTEGER NOT NULL,
	        name TEXT NOT NULL,
	        date_created INTEGER NOT NULL DEFAULT (unixepoch('now')),
	        FOREIGN KEY (owner)
	        	REFERENCES User (id)
        );"""
        super().setup(q)

    def import_data(self):
        pass

class Playlist_has_Song(Table):

    name = "Playlist_has_Song"
    location = "data/phs.csv"
    columns = {"playlist_id", "song_id", "order"}

    def setup(self):
        q = """
        CREATE TABLE Playlist_has_Song(
	        playlist_id INTEGER,
	        song_id INTEGER,
	        order_num INTEGER NOT NULL,
            PRIMARY KEY (playlist_id, song_id),
	        FOREIGN KEY (playlist_id)
	        	REFERENCES Playlist (id),
	        FOREIGN KEY (song_id)
	        	REFERENCES Song (id)
        );"""
        super().setup(q)

    def import_data(self):
        pass

def setup_db(conn):
    tables = []
    tables.append(User(conn))
    tables.append(Release(conn))
    tables.append(Song(conn))
    tables.append(Playlist(conn))
    tables.append(Playlist_has_Song(conn))

    for t in tables:
        t.setup()

    conn.commit()
    return tables