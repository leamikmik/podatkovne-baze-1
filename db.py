import csv, bcrypt

class Table:
    name = None
    location = None

    def setup(self, q):
        self.drop()
        self.conn.execute(q)
        self.import_data()

    def __init__(self, conn):
        self.conn = conn

    def import_data(self):
        with open(self.location) as f:
            data = csv.reader(f)
            columns = next(data)
            for row in data:
                self.insert(**{k: None if v == "" else v for k, v in zip(columns, row)})

    def drop(self):
        self.conn.execute(f"DROP TABLE IF EXISTS {self.name}")

    def insert(self, **values):
        q = f"INSERT INTO {self.name} ({"?, "*len(values)[:-2]}) VALUES ({"?, "*len(values)[:-2]})"
        cur = self.conn.execute(q, list(values.keys())+list(values.values()))
        return cur.lastrowid
    
class User(Table):

    name = "User"
    location = "data/user.csv"

    def setup(self):
        q = """
        CREATE TABLE User(
	        id INTEGER PRIMARY KEY,
	        name TEXT NOT NULL UNIQUE,
	        password TEXT NOT NULL,
	        date_created INTEGER NOT NULL DEFAULT (unixepoch('now'))
        );"""
        super().setup(q)

    def import_data(self):
        with open(self.location) as f:
            data = csv.reader(f)
            columns = next(data)
            for row in data:
                super().insert(**{k: None if v == "" else v for k, v in zip(columns, row)})

    def insert(self, **values):
        values["password"] = bcrypt.hashpw(values["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return super().insert(**values)
    
class Release(Table):

    name = "Release"
    location = "data/release.csv"

    def setup(self):
        q = """
        CREATE TABLE Release(
	        id INTEGER PRIMARY KEY,
	        author INTEGER NOT NULL,
	        title TEXT NOT NULL,
	        type TEXT NOT NULL CHECK ( type IN ("single", "ep", "album") ),
	        date_release INTEGER NOT NULL DEFAULT (unixepoch('now')),
	        FOREIGN KEY (author)
	        	REFERENCES User (id)
        );"""
        super().setup(q)

class Song(Table):
    
    name = "Song"
    location = "data/song.csv"

    def setup(self):
        q = """
        CREATE TABLE Release(
	        id INTEGER PRIMARY KEY,
	        author INTEGER NOT NULL,
	        title TEXT NOT NULL,
	        type TEXT NOT NULL CHECK ( type IN ("single", "ep", "album") ),
	        date_release INTEGER NOT NULL DEFAULT (unixepoch('now')),
	        FOREIGN KEY (author)
	        	REFERENCES User (id)
        );"""
        super().setup(q)

class Playlist(Table):

    name = "Playlist"
    location = "data/playlist.csv"

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

class Playlist_has_Song(Table):

    name = "Playlist_has_Song"
    location = "data/phs.csv"

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

def setup_db(conn):
    tables = []
    tables.append(User(conn))
    tables.append(Release(conn))
    tables.append(Song(conn))
    tables.append(Playlist(conn))
    tables.append(Playlist_has_Song(conn))

    for t in tables:
        t.setup()

    return tables