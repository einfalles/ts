--
--
--    schema.sql
--
--    created by: ashutosh@eemelabs.com
--    created on: june 17, 2013
--
--    creates the schema for the reachd app backend
--
--

-- define a user, people with the app and people that are just numbers
CREATE TABLE users (
    id        SERIAL PRIMARY KEY NOT NULL,
    name      varchar(100),
    email     varchar(50) UNIQUE,
    avatar    varchar(100)
);

-- define a user, people with the app and people that are just numbers
CREATE TABLE history (
    h_id          SERIAL PRIMARY KEY NOT NULL,
    uid           integer REFERENCES users(id),
    surl           varchar REFERENCES songs(yt_uri),
    created_at    timestamptz
);

-- geospatial coordinates
CREATE TABLE playlists (
   p_id          SERIAL NOT NULL,
   uo_id          integer REFERENCES users(id),
   ut_id          integer REFERENCES users(id),
   created_at    timestamptz NOT NULL,
   url           varchar(200) PRIMARY KEY UNIQUE,
   location      varchar(200)
);

-- maintain a history of coordinates
CREATE TABLE playlist_songs (
    id      SERIAL PRIMARY KEY NOT NULL,
    purl    varchar REFERENCES playlists(url),
    surl    varchar REFERENCES songs(yt_uri)
);

-- maintain a history of coordinates
CREATE TABLE bumps (
    id            SERIAL PRIMARY KEY NOT NULL,
    fr            integer REFERENCES users(id),
    too            integer REFERENCES users(id),
    created_at    timestamptz NOT NULL
);

-- manage the currently live flights
CREATE TABLE songs (
  s_id      SERIAL PRIMARY KEY NOT NULL,
  sp_uri    varchar(200) UNIQUE NOT NULL,
  track     varchar(200),
  artist    varchar(200),
  yt_uri    varchar(200)
);

CREATE TABLE zongz (
  s_id      SERIAL NOT NULL,
  sp_uri    varchar(200) UNIQUE NOT NULL,
  track     varchar(200),
  artist    varchar(200),
  yt_uri    varchar(200) UNIQUE PRIMARY KEY
);

CREATE TABLE pongz (
    id      SERIAL PRIMARY KEY NOT NULL,
    purl    varchar REFERENCES playlists(url),
    zurl    varchar REFERENCES zongz(yt_uri)
);

CREATE TABLE zistory (
    h_id          SERIAL PRIMARY KEY NOT NULL,
    uid           integer REFERENCES users(id),
    zurl           varchar REFERENCES zongz(yt_uri),
    created_at    timestamptz
);

INSERT INTO zongz (sp_uri,track,artist,yt_uri) VALUES ('1OAYKfE0YdrN7C1yLWaLJo','Hotline Bling','Drake','uxpDa-c-4Mc');
INSERT INTO zistory (uid,zurl,created_at) VALUES (1,'uxpDa-c-4Mc','2016-08-24 21:34:17.553612+00');
