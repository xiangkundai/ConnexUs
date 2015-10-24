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
from stream import Count_pic
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
                pic_count= Count_pic.query(ancestor=ndb.Key('Stream',stream.name))
                ndb.delete_multi(ndb.put_multi(pic_count))
                #print pic_count
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



        picNum_list = []
        streams_1=Stream.query(Stream.author==users.get_current_user()).order(-Stream.creattime).fetch()
        for stream in streams_1:
           pic_count= Count_pic.query(ancestor=ndb.Key('Stream',stream.name)).fetch()[0]
          # print (stream.name, pic_count.numbers)
           picNum_list.append(pic_count.numbers)
        streams = Stream.query().fetch()
        streams_2 = []
        count_list = []
        user_name = users.get_current_user().nickname()
       # url =users.create_login_url('/')
      #  if(users.get_current_user()):
            #user_name = users.get_current_user().nickname()
        url = users.create_logout_url('/')
        for stream in streams:
            if(users.get_current_user().email()in stream.subscribers):
                count=CountViews.query(CountViews.name==stream.name,ancestor=ndb.Key('User',stream.author_name)).fetch()[0]
                streams_2.append(stream)
                count_list.append(count.numbers)

        #else:
         #   self.redirect(url,permanent=False)

        template_values = {
                'user_name':user_name,
                'streams_1': streams_1,
                'streams_2': streams_2,
                'count_list': count_list,
                'url': url,
            "picNum_list":picNum_list
        }

        template = JINJA_ENVIRONMENT.get_template('management_index.html')
        self.response.write(template.render(template_values))

       #if not users.get_current_user():


# no use!!!!!!
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