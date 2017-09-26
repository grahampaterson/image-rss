from flask import Flask, render_template, request, url_for, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import datetime
import json

import parser
from helpers import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///imagerssdb.sqlite'
db = SQLAlchemy(app)

# ----------- Database Stuff --------------

class User(db.Model):
    __table_args__ = {
        'sqlite_autoincrement': True,
    }
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())
    last_login = db.Column(db.DateTime)

    def __init__(self, username, password, last_login):
        self.username = username
        self.password = password
        self.last_login = datetime.datetime.utcnow()

    def __repr__(self):
        return '<User %r>' % self.id

class FeedImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String())
    url = db.Column(db.String())
    date = db.Column(db.Integer)
    date_added = db.Column(db.DateTime)

    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    feed = db.relationship('Feed', backref=db.backref('images', lazy='dynamic'))

    def __init__(self, source, url, date, feed):
        self.source = source
        self.url = url
        self.date = date
        self.date_added = datetime.datetime.utcnow()
        self.feed = feed

    def __repr__(self):
        return '<FeedImage %r>' % self.url

class Feed(db.Model):
    __table_args__ = {
        'sqlite_autoincrement': True,
    }
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return '<Feed %r>' % self.url

class Subscriptions(db.Model):
    __table_args__ = {
        'sqlite_autoincrement': True,
    }
    id = db.Column(db.Integer, primary_key=True)

    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref=db.backref('subscriptions', lazy='dynamic'))
    feed = db.relationship('Feed')

    def __init__(self, feed, user):
        self.feed = feed
        self.user = user

    def __repr__(self):
        return '<Subscription %r>' % self.id

# ----------- Application routes Flask --------------

@app.route('/')
def index():
    user_id = request.cookies.get('id')

    # check if cookie exists and create one if it doesn't
    if user_id is None:
        new_user = new_user_db("", "")
        resp = make_response(render_template('index.html'))
        resp.set_cookie('id', str(new_user.id))
        return resp
    # if cookie exists but user doesn't exist, create new user and new cookie
    elif User.query.get(user_id) is None:
        new_user = new_user_db("", "")
        resp = make_response(render_template('index.html'))
        resp.set_cookie('id', str(new_user.id))
        return resp
    # load the users' subscriptions
    else:
        log('Found a cookie and logged in user:' + user_id)
        # tries to get user's subs
        try:
            User.query.get(user_id)
            subs = User.query.get(user_id).subscriptions
            # TODO update user last login with current date
            # TODO create new function for below code
            # select all image where image.feed = user.subscriptions.feed(each)
            images = []
            for sub in subs:
                for image in sub.feed.images:
                    images.append(image.__dict__)
            return render_template('index.html', images=images, subs=subs)
        except:
            log('Could not load the current users subscriptions with user id:' + user_id)
            return render_template('index.html', images=images, subs=subs)

# url -> (array json)
# receives an rss feed url and returns an array of json objects
@app.route('/addfeed')
def addfeed():
    url = request.args.get('url').strip()
    log('User tried to add feed with url ' + url)
    feed = url_to_db(url)
    # only returns json of new images if user isn't already subscribed
    sub = add_sub(url, request.cookies['id'])

    if sub == 2:
        log ('already subscribed to feed')
        return jsonify([])

    # some kind of join here
    sub_info = {'subid' : sub.id, 'feedurl' : sub.feed.url}

    image_list = list(map(sqlrow_to_json, feed.images.all()))
    response = {'images' : image_list, 'sub' : sub_info}
    log('Returned JSON to be added to page')
    return jsonify(response)

# TODO
# Takes a url and displays the most appropriate rss feed , from here you can added
# a subscription to your account
@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html')

# sub id -> removes subscription, integer
# removes the sub id from db and returns feed id to be removed
@app.route('/removefeed')
def removefeed():
    sub_id = request.args.get('subid')
    feed_id = remove_sub(sub_id)
    return jsonify({'feedid': feed_id, 'subid' : sub_id })

# ----------- Functions --------------

# SQLAlc Obj -> json
# takes an sqlalchemy row and converts it to a dict stripping sa instance state
def sqlrow_to_json(sqlrow):
    sqlrow = sqlrow.__dict__
    sqlrow.pop('_sa_instance_state', None)
    return sqlrow

# String, String -> SQL User objects
# Creates a new user with Username Password in the next available db position
# and returns the new user sql object
def new_user_db(username, password):
    new_user = User(username, password, 0)
    db.session.add(new_user)
    db.session.commit()
    log('A new user was created with id:' + new_user.id)
    return new_user

# SubID -> DB Subscriptions removal, feed_id
# takes a feed Id and user ID and removes the corrosponding subscription
def remove_sub(sub_id):
    sub = Subscriptions.query.get(sub_id)
    feedid = sub.feed.id
    log('User:' + str(sub.user_id) + ' removed sub with id:' + str(sub_id))
    db.session.delete(sub)
    db.session.commit()
    return feedid

# URL, user_id -> DB subscriptions entry, Int
# takes a user ID and url and adds a subscriptions entry in the database
# ASSUME. url already exists
def add_sub(url, user_id):
    feed_query = Feed.query.filter_by(url=url).first()
    user = User.query.get(user_id)

    # make sure url exists as a feed before adding a subscription
    if feed_query is None:
        log('Adding Sub: Couldnt find feed with this url in db, did not sub')
        return 1

    # make sure user is not already subscribed to feed
    if Subscriptions.query.filter((Subscriptions.feed_id == feed_query.id) & (Subscriptions.user_id == user.id)).first() is not None:
        log ('Adding Sub: Subscription already exists, did not add sub')
        return 2

    new_sub = Subscriptions(feed_query, user)
    db.session.add(new_sub)
    db.session.commit()
    return new_sub

# URL -> populates Database
# takes a rss url and populates the database with the feed and all images
# TODO
def url_to_db(url):

    # try find url and if it doesn't exist create it
    feed = Feed.query.filter_by(url=url).first()
    if (feed is None):
        feed = Feed(url)
        db.session.add(feed)

    # ImageElement -> Populate Database
    # takes an image element and adds it to the database if it's url doesn't already exist
    def ie_to_db(ie):
        # adds image if it's url doesn''t already exist in db
        check_feed = FeedImage.query.filter_by(url=ie.url).first()
        if check_feed is None:
            log('Tried to add image to db: url didnt exist, added')
            db.session.add(FeedImage(ie.source, ie.url, ie.date, feed))
        elif check_feed.feed != feed:
            log('Tried to add image to db: url existed but feed id doesnt match, added')
            db.session.add(FeedImage(ie.source, ie.url, ie.date, feed))
        else:
            log('Tried to add image to db: url exists and feeds match, didnt add')


    # (listof Imageelements) -> Populate Database
    # takes a list of image elements and adds them to the Database
    def loie_to_db(loie):
        for ie in loie:
            ie_to_db(ie)

    loie_to_db(parser.get_images(url))
    db.session.commit()
    return feed
