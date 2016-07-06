# -*- coding: utf-8 -*-
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
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://bqqytgjxunnpub:iKDOMPBtbGW_iYh3APj_J9-fdG@ec2-54-221-236-207.compute-1.amazonaws.com:5432/d2dq69kou4rdn0'

# instantiates sqlalchemy class with postgres uri
db = SQLAlchemy(app)

# creates all tables…defined where though?
db.create_all()

#
# Utilities.
#

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    # token = db.Column()
    # phone_number_id = db.Column(db.Integer, db.ForeignKey('phone_number.id'), nullable=False)
    # location_history = db.relationship('LocationHistory', backref='user', lazy='dynamic')
    # affiliation_id = db.Column(db.Integer, db.ForeignKey('affiliation.id'))
    # platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'))

    def __init__ (self, uid, name, email):
        self.uid = uid
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)

    def get_watch_history():
        return "get watch history"

class Playlist(db.Model):
    def __init__ (self):
    def __repr__(self):
        return "playlist"

class PlaylistSongs(db.Model):
    def __init__ (self):
    def __repr__(self):
        return "songs"

class Bumps(db.Model):
    def __init__ (self):
    def __repr__(self):
        return "bumps"

class ListeningHistory(db.Model):
    def __init__ (self):
    def __repr__(self):
        return "history"

class Generator():
    def __init__ (self):
    def __repr__(self):
        return "generator"
