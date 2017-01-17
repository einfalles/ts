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
    id              SERIAL PRIMARY KEY NOT NULL,
    name            varchar(200),
    avatar          varchar(200),
    lost_login      timestamptz,
    token_expiry    timestamptz
);

CREATE TABLE user_services (
    id                  SERIAL PRIMARY KEY NOT NULL,
    user_id             integer REFERENCES users(id),
    service             varchar(200),
    service_username    varchar(300),
    access_token        varchar(300),
    refresh_token       varchar(300)
);
-- define a user, people with the app and people that are just numbers
CREATE TABLE history (
    id            SERIAL PRIMARY KEY NOT NULL,
    user_id       integer REFERENCES users(id),
    spotify_id    varchar(300),
    created_at    timestamptz
);

-- geospatial coordinates
CREATE TABLE playlists (
   id          SERIAL PRIMARY KEY NOT NULL,
   sender          integer REFERENCES users(id),
   recipient          integer REFERENCES users(id),
   created_at    timestamptz NOT NULL,
   url           varchar(800)
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

CREATE TABLE dashboard (
    id              SERIAL PRIMARY KEY NOT NULL,
    valence         float4,
    energy          float4,
    popularity      integer,
    dancebility     float4,
    created_at    timestamptz NOT NULL
);

INSERT INTO zongz (sp_uri,track,artist,yt_uri) VALUES ('1OAYKfE0YdrN7C1yLWaLJo','Hotline Bling','Drake','uxpDa-c-4Mc');
INSERT INTO zistory (uid,zurl,created_at) VALUES (1,'uxpDa-c-4Mc','2016-08-24 21:34:17.553612+00');
