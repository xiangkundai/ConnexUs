import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images

from stream import Stream
from stream import Picture
from stream import CountViews

import webapp2
import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class ManagementPage(webapp2.RequestHandler):
    def get(self):
        print("test!!")
        dellsts=self.request.get_all("status")
        if (len(dellsts) > 0):
            streams=Stream.query(Stream.name.IN(dellsts), Stream.author==users.get_current_user()).fetch()
            counts=CountViews.query(CountViews.name.IN(dellsts), ancestor=ndb.Key('User', users.get_current_user().nickname())).fetch()
            for stream in streams:
                pictures=db.GqlQuery("SELECT * FROM Picture " +"WHERE ANCESTOR IS :1",db.Key.from_path('Stream',stream.name))
                db.delete(pictures)
            ndb.delete_multi(ndb.put_multi(streams))
            ndb.delete_multi(ndb.put_multi(counts))
        dellsts=self.request.get_all("status1")
        #self.response.write(len(dellsts))
        if (len(dellsts) > 0):
            streams=Stream.query(Stream.name.IN(dellsts)).fetch()
            for stream in streams:
                if(users.get_current_user() and users.get_current_user().nickname() in stream.subscribers):
                    stream.subscribers.remove(users.get_current_user().nickname())
                    stream.put()

        self.response.write(users.get_current_user())

        streams_1=Stream.query(Stream.author==users.get_current_user()).order(-Stream.creattime).fetch()
        streams = Stream.query().fetch()
        streams_2 = []
        count_list = []
        if(users.get_current_user()):
            for stream in streams:
                if(users.get_current_user().nickname() in stream.subscribers):
                    count=CountViews.query(CountViews.name==stream.name,ancestor=ndb.Key('User',stream.author_name)).fetch()[0]
                    streams_2.append(stream)
                    count_list.append(count)

        url = users.create_logout_url('/')
        template_values = {
                'streams_1': streams_1,
                'streams_2': streams_2,
                'count_list': count_list,
                'url': url
        }

        template = JINJA_ENVIRONMENT.get_template('management_index.html')
        self.response.write(template.render(template_values))

        if not users.get_current_user():
            self.redirect('/',permanent=False)


class DeleteStreams(webapp2.RequestHandler):
    def get(self):
        original_url=self.request.headers['Referer']
        dellsts=self.request.get_all("status")
        if(len(dellsts)>0):
            streams=Stream.query(Stream.name.IN(dellsts), Stream.author==users.get_current_user()).fetch()
            for stream in streams:
                pictures=db.GqlQuery("SELECT * FROM Picture " +"WHERE ANCESTOR IS :1",db.Key.from_path('Stream',stream.name))
                db.delete(pictures)
            ndb.delete_multi(ndb.put_multi(streams))
        self.redirect(original_url)

application = webapp2.WSGIApplication([
    ('/management', ManagementPage),
    ('/delstream', DeleteStreams),
], debug=True)