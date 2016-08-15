"""

ts_models.py
~~~~~~~~~~~

description
~~~~~~~~~~~
This file creates the SQLAlchemy ORM model for the tunesmash app.

metadata
~~~~~~~~
author: dn@rad.kitchen
date of creation: July 4, 2016
date of last edit:

Copyright (c) Rad Kitchen Inc. All rights reserved.

"""

import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

PRODUCTION = 'postgres://ksualenqkvlhjj:h84hpFPOi4boL6QYl6EOwRyP6T@ec2-54-243-204-195.compute-1.amazonaws.com:5432/de1brda8ltt7bd'
DEVELOPMENT = 'postgresql://localhost:5432/rachelgoree'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = PRODUCTION
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.create_all()


#
# Classes for Database Models
#
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200),index=True)
    avatar = db.Column(db.String(200))

    def __init__ (self, name, email, avatar):
        self.name = name
        self.email = email
        self.avatar = avatar

    def __repr__(self):
        return '<User %r>' % (self.email)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return self.id  # python 2
        except NameError:
            return str(self.id)  # python 3


class History(db.Model):
    __tablename__ = 'history'
    h_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.id'),index=True)
    sid = db.Column(db.Integer, db.ForeignKey('songs.s_id'))
    user = db.relationship('User', foreign_keys=[uid])
    song = db.relationship('Song', foreign_keys=[sid])
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__ (self,uid,sid,created_at):
        self.uid = uid
        self.sid = sid
        self.created_at = created_at

    def __repr__(self):
        return "history"


class Playlist(db.Model):
    __tablename__ = 'playlists'
    p_id = db.Column(db.Integer, primary_key=True)
    uo_id = db.Column(db.Integer, db.ForeignKey('users.id'),index=True)
    ut_id = db.Column(db.Integer, db.ForeignKey('users.id'),index=True)
    uone = db.relationship('User',foreign_keys=[uo_id])
    utwo = db.relationship('User',foreign_keys=[ut_id])
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    location = db.Column(db.String(200))
    url = db.Column(db.String(200))

    def __init__ (self,uo_id,ut_id,created_at,location,url):
        self.uo_id = uo_id
        self.ut_id = ut_id
        self.created_at = created_at
        self.location = location
        self.url = url

    def __repr__(self):
        return "User one: %r // User two: %r" % (self.uone, self.utwo)


class PlaylistSong(db.Model):
    __tablename__ = 'playlist_songs'
    id = db.Column(db.Integer, primary_key=True)
    pl_id = db.Column(db.Integer, db.ForeignKey('playlists.p_id'), index=True)
    s_id = db.Column(db.Integer, db.ForeignKey('songs.s_id'))
    playlist = db.relationship('Playlist', foreign_keys=[pl_id])
    song = db.relationship('Song', foreign_keys=[s_id])

    def __init__ (self,p_id, s_id):
        self.pl_id = p_id
        self.s_id = s_id

    def __repr__(self):
        return "playlist songs"


class Song(db.Model):
    __tablename__ = 'songs'
    s_id = db.Column(db.Integer, primary_key=True)
    track = db.Column(db.String(200))
    artist = db.Column(db.String(200))
    yt_uri = db.Column(db.String(200))
    sp_uri = db.Column(db.String(200),index=True)

    def __init__ (self,sp_uri,track,artist,yt_uri):
        self.sp_uri = sp_uri
        self.track = track
        self.artist = artist
        self.yt_uri = yt_uri

    def __repr__(self):
        return "Song"

#
# HELPER FUNCTIONS
#
def get_user(email=None,uid=None):
    if email:
        return User.query.filter(User.email==email).first()
    if uid:
        return User.query.filter(User.id==uid).first()
    else:
        return None

def get_all_playlists(user_id=None,user_email=None):
    playlists = []
    user_id = int(user_id)
    if user_id:
        result = Playlist.query.filter(db.or_(Playlist.uo_id==user_id, Playlist.ut_id==user_id)).all()
        for i in result:
            user = get_user(uid=user_id)
            playlists.append((i.p_id,user.id,user.name,user.email,i.created_at,i.url))
        db.session.close()
        return result

    if user_email:
        user = User.query.filter_by(email=user_email).first()
        user_id = user.id
        result = Playlist.query.filter(db.or_(Playlist.uone==user_id, Playlist.utwo==user_id)).all()
        db.session.close()
        return result
    return None


def get_playlist_songs(pl_id=None):
    songs = []
    if pl_id:
        playlist = PlaylistSong.query.filter(PlaylistSong.pl_id==pl_id).all()
        for i in playlist:
            song = Song.query.filter(Song.id==i.s_id).first()
            songs.append((song.track, song.artist, song.yt_uri, song.spotify_uri))
    else:
        return None
    return songs


def get_playlist_url(pl_id=None):
    if pl_id:
        url = Playlist.query.filter(Playlist.id==pl_id).first()
        return url
    else:
        return None


def get_history(uid=None,uemail=None):
    if uid:
        results = History.query.filter_by(uid=uid).first()
        return results
    else:
        return None
