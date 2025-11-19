CREATE TABLE User(
	id INTEGER PRIMARY KEY,
	name TEXT NOT NULL UNIQUE,
	password TEXT NOT NULL,
	date_created INTEGER NOT NULL DEFAULT (unixepoch('now'))
);

CREATE TABLE Release(
	id INTEGER PRIMARY KEY,
	author INTEGER NOT NULL,
	title TEXT NOT NULL,
	type TEXT NOT NULL CHECK ( type IN ("single", "ep", "album") ),
	date_release INTEGER NOT NULL DEFAULT (unixepoch('now')),
	FOREIGN KEY (author)
		REFERENCES User (id)
);

CREATE TABLE Song(
    id INTEGER PRIMARY KEY,
    release INTEGER NOT NULL,
    order_num INTEGER NOT NULL,
    title TEXT NOT NULL,
    length INTEGER NOT NULL,
    FOREIGN KEY (release)
    	REFERENCES Release (id)
);

CREATE TABLE Playlist(
	id INTEGER PRIMARY KEY,
	owner INTEGER NOT NULL,
	name TEXT NOT NULL,
	date_created INTEGER NOT NULL DEFAULT (unixepoch('now')),
	FOREIGN KEY (owner)
		REFERENCES User (id)
);

CREATE TABLE Playlist_has_Song(
	playlist_id INTEGER,
	song_id INTEGER,
	order_num INTEGER NOT NULL,
    PRIMARY KEY (playlist_id, song_id),
	FOREIGN KEY (playlist_id)
		REFERENCES Playlist (id),
	FOREIGN KEY (song_id)
		REFERENCES Song (id)
);
