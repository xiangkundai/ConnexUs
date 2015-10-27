import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2
from google.appengine.ext import db


class Stream(ndb.Model):

    name=ndb.StringProperty()
    tag=ndb.StringProperty(repeated=True,default=None)
    subscribers=ndb.StringProperty(repeated=True)
    url=ndb.StringProperty()
    guesturl=ndb.StringProperty()
    creattime=ndb.DateTimeProperty(auto_now_add=True)
    lastnewdate = ndb.DateTimeProperty(auto_now_add=True)
    numberofpictures=ndb.IntegerProperty()
    total=ndb.IntegerProperty()
    #views=ndb.IntegerProperty()
    coverurl=ndb.StringProperty()
    author=ndb.UserProperty()
    author_name=ndb.StringProperty()
    #author=ndb.stringProperty()

class Picture(db.Model):
    imgkey = db.StringProperty()
    caption = db.StringProperty(default="Hi there, I am a picture!")
    #blob_key = db.BlobKeyProperty()
    uploaddate= db.DateTimeProperty(auto_now_add=True)
    loc = db.GeoPtProperty(required=True,default=db.GeoPt(0,0))


class Global(ndb.Model):
    name=ndb.StringProperty()
    count=ndb.IntegerProperty()
    limit=ndb.IntegerProperty()

class CountViews(ndb.Model):
    name=ndb.StringProperty()
    numbers=ndb.IntegerProperty()
    totalviews=ndb.IntegerProperty()

class Count_pic(ndb.Model):
    numbers = ndb.IntegerProperty()

class stream_name_set(ndb.Model):
    name = ndb.StringProperty()





