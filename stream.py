import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2
from google.appengine.ext import db


class Stream(ndb.Model):

    name=ndb.StringProperty()
    tag=ndb.StringProperty(repeated=True)
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
    imgkey=db.StringProperty()
    uploaddate= db.DateTimeProperty(auto_now_add=True)

class Global(ndb.Model):
    name=ndb.StringProperty()
    count=ndb.IntegerProperty()
    limit=ndb.IntegerProperty()

class CountViews(ndb.Model):
    name=ndb.StringProperty()
    numbers=ndb.IntegerProperty()
    totalviews=ndb.IntegerProperty()