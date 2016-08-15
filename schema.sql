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
    h_id    SERIAL PRIMARY KEY NOT NULL,
    uid           integer REFERENCES users(id),
    sid           integer REFERENCES songs(s_id),
    created_at    timestamptz
);

-- geospatial coordinates
CREATE TABLE playlist (
   p_id         SERIAL PRIMARY KEY NOT NULL,
   uone          integer REFERENCES users(id),
   utwo          integer REFERENCES users(id),
   created_at    timestampz NOT NULL DEFAULT,
   url           varchar(200) UNIQUE,
   location      varchar(200)
);

-- maintain a history of coordinates
CREATE TABLE playlist_songs (
    pl_id   integer REFERENCES playlist(p_id),
    s_id    integer REFERENCES song(s_id)
);

-- manage the currently live flights
CREATE TABLE songs (
  s_id      SERIAL PRIMARY KEY NOT NULL,
  sp_uri    varchar(200) UNIQUE NOT NULL,
  track     varchar(200),
  artist    varchar(200),
  yt_uri    varchar(200)
);
