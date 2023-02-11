-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/XX53uP
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.


CREATE TABLE "User" (
    "id" INT NOT NULL,
    "username" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "user_img" TEXT NULL,
    CONSTRAINT "pk_User" PRIMARY KEY (
        "id"
     ),
    CONSTRAINT "uc_User_email" UNIQUE (
        "email"
    )
);

CREATE TABLE "Playlist" (
    "id" INT NOT NULL,
    "user" INT NOT NULL,
    "user_img" TEXT NOT NULL,
    "playlist_name" TEXT NOT NULL,
    CONSTRAINT "pk_Playlist" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Songs" (
    "id" INT NOT NULL,
    "track_id" TEXT NOT NULL,
    "track_name" TEXT NOT NULL,
    "track_uri" TEXT NOT NULL,
    "artist" TEXT NOT NULL,
    "tempo" FLOAT NOT NULL,
    "time_sig" INT NOT NULL,
    "key" INT NOT NULL,
    "mode" INT NOT NULL,
    "duration" INT NOT NULL,
    "loudness" INT NOT NULL,
    CONSTRAINT "pk_Songs" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Playlist_Song" (
    "playlist_id" INT NOT NULL,
    "song_id" INT NOT NULL
);

CREATE TABLE "Artist" (
    "id" INT NOT NULL,
    "spotify_artist_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    CONSTRAINT "pk_Artist" PRIMARY KEY (
        "id"
     )
);

CREATE TABLE "Artist_song" (
    "song_id" INT NOT NULL,
    "artist_id" TEXT NOT NULL
);

ALTER TABLE "User" ADD CONSTRAINT "fk_User_id" FOREIGN KEY("id")
REFERENCES "Playlist" ("user");

ALTER TABLE "Playlist" ADD CONSTRAINT "fk_Playlist_id" FOREIGN KEY("id")
REFERENCES "Playlist_Song" ("playlist_id");

ALTER TABLE "Songs" ADD CONSTRAINT "fk_Songs_id" FOREIGN KEY("id")
REFERENCES "Artist_song" ("song_id");

ALTER TABLE "Songs" ADD CONSTRAINT "fk_Songs_artist" FOREIGN KEY("artist")
REFERENCES "Artist" ("id");

ALTER TABLE "Playlist_Song" ADD CONSTRAINT "fk_Playlist_Song_song_id" FOREIGN KEY("song_id")
REFERENCES "Songs" ("id");

ALTER TABLE "Artist_song" ADD CONSTRAINT "fk_Artist_song_artist_id" FOREIGN KEY("artist_id")
REFERENCES "Artist" ("id");

