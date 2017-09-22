from flask import Flask, render_template, request, url_for, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import datetime
import json

import parser

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

    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    feed = db.relationship('Feed', backref=db.backref('images', lazy='dynamic'))

    def __init__(self, source, url, date, feed):
        self.source = source
        self.url = url
        self.date = date
        self.feed = feed

    def __repr__(self):
        return '<FeedImage %r>' % self.url

class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return '<Feed %r>' % self.url

class Subscriptions(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref=db.backref('subscriptions', lazy='dynamic'))
    feed = db.relationship('Feed')

    def __init__(self, feed, user):
        self.feed = feed
        self.user = user

    def __repr__(self):
        return '<Subscription %r>' % self.user_id

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
        print('found cookie')
        # tries to get user's subs
        try:
            User.query.get(user_id)
            # TODO update user last login with current date
            # TODO create new function for below code
            # select all image where image.feed = user.subscriptions.feed(each)
            images = []
            for sub in User.query.get(user_id).subscriptions:
                for image in sub.feed.images:
                    images.append(image.__dict__)
            return render_template('index.html', images=images)
        except:
            print('found user but could not load subscriptions')
            return render_template('index.html', images=images)

# url -> (array json)
# receives an rss feed url and returns an array of json objects
@app.route('/addfeed')
def addfeed():
    url = request.args.get('url').strip()
    feed = url_to_db(url)
    # only returns json of new images if user isn't already subscribed
    if add_sub(url, request.cookies['id']) == 2:
        print ('already subscribed to feed')
        return jsonify([])

    return jsonify(list(map(sqlrow_to_json, feed.images.all())))

# feed id -> removes subscription
@app.route('/removefeed')
def removefeed():
    remove_sub(request.args.get('feedid'), request.cookies['id'])
    return []

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
    print('made new user')
    return new_user

# FeedID, user_id -> DB Subscriptions removal, int
# takes a feed Id and user ID and removes the corrosponding subscription
def remove_sub(feed_id, user_id):
    sub = Subscriptions.query.filter_by(feed_id=feed_id).filter_by(user_id=user_id).first()
    db.session.delete(sub)
    db.session.commit()

# URL, user_id -> DB subscriptions entry, Int
# takes a user ID and url and adds a subscriptions entry in the database
# ASSUME. url already exists
def add_sub(url, user_id):
    feed_query = Feed.query.filter_by(url=url).first()
    user = User.query.get(user_id)

    # make sure url exists as a feed before adding a subscription
    if feed_query is None:
        print('Couldnt find feed with this url in db, did not sub')
        return 1

    # make sure user is not already subscribed to feed
    if Subscriptions.query.filter((Subscriptions.feed_id == feed_query.id) & (Subscriptions.user_id == user.id)).first() is not None:
        print ('Subscription already exists, did not add sub')
        return 2

    new_sub = Subscriptions(feed_query, user)
    db.session.add(new_sub)
    db.session.commit()
    return 0

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
            print('url didnt exist, added')
            db.session.add(FeedImage(ie.source, ie.url, ie.date, feed))
        elif check_feed.feed != feed:
            print('feeds dont match, added')
            db.session.add(FeedImage(ie.source, ie.url, ie.date, feed))
        else:
            print('url exists and feeds match, didnt add')


    # (listof Imageelements) -> Populate Database
    # takes a list of image elements and adds them to the Database
    def loie_to_db(loie):
        for ie in loie:
            ie_to_db(ie)

    loie_to_db(parser.get_images(url))
    db.session.commit()
    return feed
