import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db
import webapp2
from stream import Stream
from stream import Picture

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import images
import jinja2
import os
import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class viewStreams(webapp2.RequestHandler):
  def get(self):

    #Change!# streams=Stream.query(Stream.author==users.get_current_user()).order(-Stream.creattime).fetch()
    all_streams=Stream.query().order(-Stream.creattime).fetch()
    user_name = ""

    if users.get_current_user():
        user_name = users.get_current_user().nickname()
        print "yes!"
        print  users.get_current_user().email()

    template_values = {
                'user_name': user_name,
                'all_streams': all_streams,
        }

    template = JINJA_ENVIRONMENT.get_template('view_index.html')
    self.response.write(template.render(template_values))

class viewAllPhotos(webapp2.RequestHandler):
    def get(self):
        all_streams=Stream.query().order(-Stream.creattime).fetch()
        cover_url_list = []
        stream_list = []
        for stream in all_streams:
            stream_list.append(stream.name)
            cover_url_list.append(stream.coverurl)

        dictPassed = {'displayCovers':cover_url_list, 'streamList':stream_list}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)

class mySubscribe(webapp2.RequestHandler):
    def post(self):
        email = self.request.get("email")
        print (type(email))
      #  location = email.find("@")
       # user = email[:location]
   #     print "user: "+user
        final_picture = []
     #   first_flag = True
        displayImages = []
        streams = Stream.query().fetch()
        print streams
        print streams[0]
        #print type(users.get_current_user().nickname())

        print users.get_current_user()
     #   for stream in streams:

      #      if(users.get_current_user().nickname() in stream.subscribers):
       #         print stream.name
        for stream in streams:
            #print "user0: "+user
           # print type(user)
            print stream.subscribers
            #print type(stream.subscribers[0])
            if(email in stream.subscribers):
              #  print "user1: "+user
                pictures=db.GqlQuery("SELECT *FROM Picture " + "WHERE ANCESTOR IS :1 " +"ORDER BY uploaddate DESC" , db.Key.from_path('Stream',stream.name))
                for pic in pictures:
                    if len(final_picture) < 16:
                      #  print ("user2",pic.uploaddate)
                     #   print("user2",pic.imgkey)
                        final_picture.append(pic)
                        continue
                    else:
                   #     print "user3: "+user
                        if pic.uploaddate > final_picture[15].uploaddate:
                            final_picture.pop()
                            final_picture.append(pic)
                            final_picture.sort(key=lambda pic:pic.uploaddate, reverse=True)

        final_picture.sort(key=lambda pic:pic.uploaddate, reverse=True)
        for f_pic in final_picture:
            #print f_pic.uploaddate
            displayImages.append("http://connexus2-1095.appspot.com/img?img_id="+str(f_pic.key()))
           # print f_pic.uploaddate


        dictPassed = {'displayImages':displayImages}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)






application = webapp2.WSGIApplication([
    ('/viewallstreams', viewStreams),
    ('/viewAllPhotos',viewAllPhotos),
    ('/mySubscribe',mySubscribe)
], debug=True)