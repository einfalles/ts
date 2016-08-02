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
PRODUCTION = 'postgres://ksualenqkvlhjj:h84hpFPOi4boL6QYl6EOwRyP6T@ec2-54-243-204-195.compute-1.amazonaws.com:5432/de1brda8ltt7bd'
DEVELOPMENT = 'postgresql://localhost:5432/rachelgoree'
import datetime
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = PRODUCTION
db = SQLAlchemy(app)
db.create_all()


# Extend the functionality of the Model class.
def create(self):
    """ Adds a model object and commits it. """
    db.session.add(self)
    if self in db.session.new and len(db.session.new) <= 1:
        db.session.commit()
        return self
    else:
        return None

# Deletes and a model from the object then commits the change.
def destroy(self):
    """ Deletes a model object and commits it. """
    db.session.delete(self)
    db.session.commit()

# Wrapper for session.commit() so that we don't import db.
def synch(self):
    """ Commits a model object """
    db.session.commit()

# Bind the functions to the Model class.
db.Model.create = create
db.Model.destory = destroy
db.Model.synch = synch


#
# Classes for Database Models
#
class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    def __init__ (self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)

    def get_watch_history():
        return "get watch history"

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
    __tablename__ = 'History'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('User.id'))
    sid = db.Column(db.Integer, db.ForeignKey('Song.id'))
    user_id = relationship('User', foreign_keys=[uid])
    song_id = relationship('Song', foreign_keys=[sid])
    time = db.Column(db.BigInteger)
    

    def __init__ (self,uid,sid,time):
        self.uid = uid
        self.sid = sid
        self.time = time

    def __repr__(self):
        return "history"

def get_history(uid=None,uemail=None):
    if uid:
        results = History.query.filter_by(uid=uid).order_by(History.time.desc()).first()
        return results
    else:
        return None

class Playlist(db.Model):
    __tablename__ = 'Playlist'
    id = db.Column(db.Integer, primary_key=True)
    uone = db.Column(db.Integer, db.ForeignKey('User.id'))
    utwo = db.Column(db.Integer, db.ForeignKey('User.id'))
    time = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow())
    location = db.Column(db.String(100))
    url = db.Column(db.String(100))

    def __init__ (self,uone,utwo,time,location,url):
        self.uone = uone
        self.utwo = utwo
        self.time = time
        self.location = location
        self.url = url

    def __repr__(self):
        return "User one: %r // User two: %r" % (self.uone, self.utwo)

class PlaylistSong(db.Model):
    __tablename__ = 'PlaylistSong'
    id = db.Column(db.Integer, primary_key=True)
    pl_id = db.Column(db.Integer, db.ForeignKey('Playlist.id'))
    song_id = db.Column(db.Integer, db.ForeignKey('Song.id'))
    def __init__ (self,pl_id, song_id):
        self.pl_id = pl_id
        self.song_id = song_id

    def __repr__(self):
        return "playlist songs"

class Song(db.Model):
    __tablename__ = 'Song'
    id = db.Column(db.Integer, primary_key=True)
    spotify_uri = db.Column(db.String(100))
    track = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    yt_uri = db.Column(db.String(100))

    def __init__ (self,spotify_uri,track,artist,yt_uri):
        self.spotify_uri = spotify_uri
        self.track = track
        self.artist = artist
        self.yt_uri = yt_uri

    def __repr__(self):
        return "Song"

def get_user(email=None,uid=None):
    """ Return a User if one is associated with user.id or PhoneNumber. """
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
        result = Playlist.query.filter(db.or_(Playlist.uone==user_id, Playlist.utwo==user_id)).all()
        for i in result:
            match = 0
            if i.uone == user_id:
                match = i.utwo
            if i.utwo == user_id:
                match = i.uone
            user = get_user(uid=match)
            playlists.append((i.id,user.id,user.name,user.email,i.time,i.url))
        db.session.close()
        return playlists

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
            song = Song.query.filter(Song.id==i.song_id).first()
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