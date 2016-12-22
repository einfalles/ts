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
import pprint
import psycopg2
import datetime
from dateutil.parser import parse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
PRODUCTION = 'postgres://ksualenqkvlhjj:h84hpFPOi4boL6QYl6EOwRyP6T@ec2-54-243-204-195.compute-1.amazonaws.com:5432/de1brda8ltt7bd'
DEVELOPMENT = 'postgresql://localhost:5432'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = PRODUCTION
# app.config['SQLALCHEMY_DATABASE_URI'] = DEVELOPMENT
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 20
db = SQLAlchemy(app)
db.create_all()


#
# Classes for Database Models
#
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    avatar = db.Column(db.String(200))
    lost_login = db.Column(db.DateTime())
    token_expiry = db.Column(db.DateTime())

    def __init__ (self, name, token_expiry,avatar , lost_login):
        self.name = name
        self.avatar = avatar
        self.lost_login = lost_login
        self.token_expiry = token_expiry

    def __repr__(self):
        return '<User %r>' % (self.name)

    def get_id(self):
        try:
            return self.id  # python 2
        except NameError:
            return str(self.id)  # python 3

class UserService(db.Model):
    __tablename__ = 'user_services'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),index=True)
    service = db.Column(db.String(200))
    service_username = db.Column(db.String(300))
    access_token = db.Column(db.String(300))
    refresh_token = db.Column(db.String(300))
    user_relationship = db.relationship('User', foreign_keys=[user_id])

    def __init__ (self, user_id, service,service_username,access_token,refresh_token):
        self.user_id = user_id
        self.service = service
        self.service_username = service_username
        self.access_token = access_token
        self.refresh_token = refresh_token

    def __repr__(self):
        return '<User %r>' % (self.user_relationship.name)

    def get_id(self):
        try:
            return self.id  # python 2
        except NameError:
            return str(self.id)  # python 3


class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),index=True)
    spotify_id = db.Column(db.String(300))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    user_relationship = db.relationship('User', foreign_keys=[user_id])

    def __init__ (self,user_id,spotify_id,created_at):
        self.user_id = user_id
        self.spotify_id = spotify_id
        self.created_at = created_at

    def __repr__(self):
        return "hi"


class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer, db.ForeignKey('users.id'),index=True)
    recipient = db.Column(db.Integer, db.ForeignKey('users.id'),index=True)
    sender_relationship = db.relationship('User',foreign_keys=[sender])
    recipient_relationship = db.relationship('User',foreign_keys=[recipient])
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    url = db.Column(db.String(800))

    def __init__ (self,sender,recipient,created_at,url):
        self.sender = sender
        self.recipient = recipient
        self.created_at = created_at
        self.url = url

    def __repr__(self):
        return "yeah"


class PlaylistSong(db.Model):
    __tablename__ = 'playlist_songs'
    id = db.Column(db.Integer, primary_key=True)
    purl = db.Column(db.Integer, db.ForeignKey('playlists.url'), index=True)
    surl = db.Column(db.Integer, db.ForeignKey('songs.yt_uri'))
    playlist = db.relationship('Playlist', foreign_keys=[purl])
    song = db.relationship('Song', foreign_keys=[surl])

    def __init__ (self,purl, surl):
        self.purl = purl
        self.surl = surl

    def __repr__(self):
        return "playlist songs"


class Song(db.Model):
    __tablename__ = 'songs'
    s_id = db.Column(db.Integer)
    track = db.Column(db.String(200))
    artist = db.Column(db.String(200))
    yt_uri = db.Column(db.String(200),primary_key=True)
    sp_uri = db.Column(db.String(200),index=True)

    def __init__ (self,sp_uri,track,artist,yt_uri):
        self.sp_uri = sp_uri
        self.track = track
        self.artist = artist
        self.yt_uri = yt_uri

    def __repr__(self):
        return "Song"

class Bump(db.Model):
    __tablename__ = 'bumps'
    id = db.Column(db.Integer, primary_key=True)
    # first = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    # second = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    fr = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    too = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__ (self,fr,too,created_at):
        self.fr = fr
        self.too = too
        self.created_at = created_at

    def __repr__(self):
        return "Bump bump bump"

# ~~~~~~~~~~~~~~~~~
#
# HELPER FUNCTIONS
#
# ~~~~~~~~~~~~~~~~~
def get_user(uid=None,service_username=None):

    if uid:
        user = User.query.get(uid)

        if user != None:
            results = {
                'id': user.id,
                'avatar': user.avatar,
                'token_expiry': user.token_expiry,
                'name': user.name
            }
            return results
        else:
            return None

def does_user_exist(service_username=None):
    a = db.session.query(UserService).filter(UserService.service_username==service_username).all()
    if len(a) > 0:
        return a[0].user_id
    else:
        return None
def get_full_user(uid=None):
    user = db.session.query(UserService).filter(UserService.user_id==uid).all()
    song = db.session.query(History).filter(History.user_id==uid).first()
    result = row2dict(user[0].user_relationship)
    result['lost_login'] = user[0].user_relationship.lost_login
    result['token_expiry'] = user[0].user_relationship.token_expiry
    for i in user:
        us = row2dict(i)
        us.pop('id')
        result[us['service']] = us
    result['history'] = song.spotify_id
    return result

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d
def get_all_playlists(uid=None,user_email=None):
    playlists = []
    uid = int(uid)
    if uid:
        result = Playlist.query.filter(Playlist.sender==uid).all()

        for i in result:
            playlists.append({
                    'playlist_id': i.id,
                    'url': i.url,
                    'created_at': i.created_at.date().isoformat(),
                    'recipient': {'name':i.recipient_relationship.name,'avatar':i.recipient_relationship.avatar},
                    'sender': {'name':i.sender_relationship.name}
                }
            )
        db.session.close()
        return playlists

    if user_email:
        user = User.query.filter_by(email=user_email).first()
        user_id = user.id
        result = Playlist.query.filter(db.or_(Playlist.uone==user_id, Playlist.utwo==user_id)).all()
        db.session.close()
        return result
    return None

def get_pongz(purl=None):
    songs = []
    if purl:
        result = Pongz.query.filter(Pongz.purl==purl).all()
        for i in result:
            songs.append({
                # 'art': i.song.art,
                'uone': {
                    'id':i.playlist.uone.id,
                    'name':i.playlist.uone.name,
                    'avatar':i.playlist.uone.avatar,
                    'email':i.playlist.uone.email
                },
                'utwo':{
                    'id':i.playlist.utwo.id,
                    'name':i.playlist.utwo.name,
                    'avatar':i.playlist.utwo.avatar,
                    'email':i.playlist.utwo.email
                },
                'track': i.zong.track,
                'artist': i.zong.artist,
                'yt_url': i.zong.yt_uri
            })
        return songs
    else:
        return None

def get_playlist_songs(pl_id=None):
    songs = []
    if pl_id:
        result = PlaylistSong.query.filter(PlaylistSong.pl_id==pl_id).all()
        for i in result:
            songs.append({
                # 'art': i.song.art,
                'uone': {
                    'id':i.playlist.uone.id,
                    'name':i.playlist.uone.name,
                    'avatar':i.playlist.uone.avatar,
                    'email':i.playlist.uone.email
                },
                'utwo':{
                    'id':i.playlist.utwo.id,
                    'name':i.playlist.utwo.name,
                    'avatar':i.playlist.utwo.avatar,
                    'email':i.playlist.utwo.email
                },
                'track': i.song.track,
                'artist': i.song.artist,
                'yt_url': i.song.yt_uri
            })
        return songs
    else:
        return None


def get_history(uid=None,uemail=None):
    if uid:
        results = History.query.order_by('created_at desc').filter(History.uid==uid).first()
        history = {
            'sp_uri': results.song.sp_uri,
            'created_at': results.created_at.isoformat(),
            's_id': results.song.s_id,
            'yt_uri': results.song.yt_uri,
            'artist': results.song.artist,
            'track': results.song.track
        }
        return history
    else:
        return None

def zzzistory(one=None,two=None):
    histories = Zistory.query.order_by('created_at desc').filter(db.or_(Zistory.uid==one,Zistory.uid==two)).all()
    passback = {}
    for results in histories:
        if results.uid in passback:
            pass
        else:
            passback[results.uid] = {
                'sp_uri': results.song.sp_uri,
                'created_at': results.created_at.isoformat(),
                's_id': results.song.s_id,
                'yt_uri': results.song.yt_uri,
                'artist': results.song.artist,
                'track': results.song.track
            }
    return passback

def get_faster_history(one=None,two=None):
    histories = History.query.order_by('created_at desc').filter(db.or_(History.uid==one,History.uid==two)).all()
    passback = {}
    for results in histories:
        if results.uid in passback:
            pass
        else:
            passback[results.uid] = {
                'sp_uri': results.song.sp_uri,
                'created_at': results.created_at.isoformat(),
                's_id': results.song.s_id,
                'yt_uri': results.song.yt_uri,
                'artist': results.song.artist,
                'track': results.song.track
            }
    return passback


def song_run(songs,pl):
    new = []
    plob = []
    print("*** SONG RUN ***")
    for s in songs:
        try:
            sp_match = db.session.query(db.exists().where(
                    Zong.sp_uri == s[2]
            )).scalar()
            yt_match =  db.session.query(db.exists().where(
                    Zong.yt_uri == s[3]
            )).scalar()
            print('Song: {0} // SP URI: {1} // YT URI: {2} // Sp Exists: {3} // Yt Exists: {4}'.format(s[0],s[2],s[3],sp_match, yt_match))
            if sp_match == True and yt_match == True:
                # print('*** This song is already in the db {0}'.format(s))
                plob.append(Pongz(pl,s[3]))
            if sp_match == False and yt_match == False:
                # print('New song {0}'.format(s))
                new.append(Zong(track=s[0],artist=s[1],sp_uri=s[2],yt_uri=s[3]))
                plob.append(Pongz(pl,s[3]))
            if sp_match == True and yt_match == False:
                # print('Spotify URI is there, but not yt uri {0}'.format(s))
                a = Zong.query.filter(Zong.sp_uri == s[2]).first()
                plob.append(Pongz(pl,a.yt_uri))
            if sp_match == False and yt_match == True:
                # print('YR URI is there but not sp...should send a log {0}'.format(s))
                plob.append(Pongz(pl,s[3]))

        except exc.IntegrityError as err:
            print("*** Integrity Error as song run: {0}".format(sys.exc_info()))
            pass
        except:
            db.session.rollback()
            pass
    db.session.add_all(new)
    db.session.add_all(plob)
    db.session.commit()

def psyco_get_user(user_id=None):
    host = 'ec2-54-243-204-195.compute-1.amazonaws.com'
    database = 'de1brda8ltt7bd'
    user = 'ksualenqkvlhjj'
    port = 5432
    password = 'h84hpFPOi4boL6QYl6EOwRyP6T'
    connection_string = "host={0} dbname={1} user={2} port={3} password={4}".format(host,database,user,port,password)
    query = 'SELECT * FROM users WHERE id={0};'.format(user_id)
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute(query)
    a = cursor.fetchone()
    results = {
        'id': a[0],
        'name': a[1],
        'email': a[2],
        'avatar': a[3]
    }
    return results
def sqlalchemy_raw_get_user(user_id=None):
    query = 'SELECT * FROM users WHERE id={0};'.format(user_id)
    r = db.engine.execute(query)
    a = r.first()
    results = {
        'id': a[0],
        'name': a[1],
        'email': a[2],
        'avatar': a[3]
    }
    return results
