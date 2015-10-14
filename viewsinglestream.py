import cgi
import urllib
import re
import time

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db

import webapp2

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import images
from google.appengine.api import urlfetch

from stream import Stream
from stream import Picture
from stream import CountViews
from stream import Count_pic


import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class UploadUrlHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write('"' + upload_url + '"')



class  ViewSinglePage(webapp2.RequestHandler):
    def get(self):
        status = (0,0)

        stream_name=re.findall('%3D(.*)',self.request.url)[0]

        #Change!# stream=Stream.query(Stream.name==stream_name, Stream.author==users.get_current_user()).fetch()[0]
        stream=Stream.query(Stream.name==stream_name).fetch()[0]

        if(stream.author==users.get_current_user()):
            status = (1,1)
        elif(users.get_current_user()):
            status = (1,0)
        else:
            self.redirect(users.create_login_url(self.request.url))

        pictures=db.GqlQuery("SELECT *FROM Picture " + "WHERE ANCESTOR IS :1 " +"ORDER BY uploaddate DESC LIMIT 3" , db.Key.from_path('Stream',stream_name))

        #print pictures[0].imgkey
        uploadurl = blobstore.create_upload_url('/upload')
        showmoreurl=urllib.urlencode({'showmore': stream.name+"=="+users.get_current_user().nickname()})
        template_values = {
                        'showmoreurl': showmoreurl,
                        'stream_name': stream_name,
                        'pictures':pictures,
                        'status':status,
                       'uploadurl':uploadurl
                     }
        template = JINJA_ENVIRONMENT.get_template('viewsinglestream_index.html')
        self.response.write(template.render(template_values))

class Image(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        picture = db.get(self.request.get('img_id'))
        blob_info = blobstore.BlobInfo.get(picture.imgkey)
        self.send_blob(blob_info)



class Upload(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        print('1')
        original_url=self.request.headers['Referer']
        img=self.get_uploads()[0]

        stream_name=re.findall('=(.*)',original_url)[0]
       # print(len(img))
     #   for img in imgs:
        if Stream.author==users.get_current_user():
            stream=Stream.query(Stream.name==stream_name, Stream.author==users.get_current_user()).fetch()[0]
            #for img in imgs:
            print('3')
            picture=Picture(parent=db.Key.from_path('Stream',stream_name))
            stream.lastnewdate= picture.uploaddate
            pic_count= Count_pic.query(ancestor=ndb.Key('Stream',stream_name)).fetch()[0]
          #  print(pic_counts)
           # for pic_count in pic_counts:
            pic_count.numbers=pic_count.numbers+1
            pic_count.put()
            print (stream)
            print (pic_count.numbers)
            print (stream.numberofpictures)
            print (stream.total)
            stream.numberofpictures=pic_count.numbers
            stream.total=stream.total+1
            #picture.id=str(stream.total)
           # img=images.resize(img,300,300)
            picture.imgkey=str(img.key())
            picture.put()
            stream.put()
            print('!!')
            print (stream.numberofpictures)
            print (stream.total)
            #time.sleep(5.0)
        else:
            self.response.out.write('<h2 >Action not allowed!</h2>')
        print('5')
        self.redirect(original_url)


class DeletePictures(webapp2.RequestHandler):
    def post(self):
        original_url=self.request.headers['Referer']
        stream_name=re.findall('=(.*)%3D%3D',original_url)[0]
        stream=Stream.query(Stream.name==stream_name, Stream.author==users.get_current_user()).fetch()[0]
        dellsts=self.request.get_all("status")
        print dellsts
        pictures=db.GqlQuery("SELECT * FROM Picture " +"WHERE ANCESTOR IS :1 AND imgkey IN :2",db.Key.from_path('Stream',stream_name),dellsts)
        for picture in pictures:
            blobstore.delete(picture.imgkey)
        db.delete(pictures)
        pic_count= Count_pic.query(ancestor=ndb.Key('Stream',stream_name)).fetch()[0]
          #  print(pic_counts)
           # for pic_count in pic_counts:
        pic_count.numbers=pic_count.numbers - len(dellsts)
        pic_count.put()
        stream.numberofpictures=pic_count.numbers
        stream.put()
        self.redirect(original_url)

class SubscribeStream(webapp2.RequestHandler):
    def post(self):
        original_url0 = self.request.headers['Referer']
        original_url = original_url0
        if "%3D" not in original_url:
            original_url += '%3D%3D'
            original_url += users.get_current_user().nickname()

        stream_name=re.findall('=(.*)%3D%3D',original_url)
        if(len(stream_name)<1):
            stream_name=re.findall('%3D(.*)%3D%3D',original_url)[0]
        else:
            stream_name=stream_name[0]

        user_name=re.findall('%3D%3D(.*)\?',original_url)
        if(len(user_name)<1):
            user_name=re.findall('%3D%3D(.*)',original_url)[0]
        else:
            user_name=user_name[0]

        user_name=user_name.split('%40')
        if(len(user_name)>1):
            user_name=user_name[0]+'@'+user_name[1]
        else:
            user_name=user_name[0]

        #Change!# stream=Stream.query(Stream.name==stream_name, Stream.author_name==user_name).fetch()[0]
        stream=Stream.query(Stream.name==stream_name).fetch()[0]

        if users.get_current_user():
            stream.subscribers.append(users.get_current_user().nickname())
        stream.put()

        self.redirect(original_url0)


class ShowPictures(webapp2.RequestHandler):
    def get(self):
        #self.response.write(users.get_current_user())
        stream_name=re.findall('%3D(.*)%3D%3D',self.request.url)[0]
        user_name=re.findall('%3D%3D(.*)',self.request.url)[0]
        infos = []
        status = (0,0)
        index=0
        url = ""
        #Change!# stream=Stream.query(Stream.name==stream_name, Stream.author_name==user_name).fetch()[0]

        pictures=db.GqlQuery("SELECT * FROM Picture " +"WHERE ANCESTOR IS :1 "+"ORDER BY uploaddate DESC",db.Key.from_path('Stream',stream_name))

        stream = Stream.query(Stream.name==stream_name).fetch()[0]


        if(users.get_current_user() and stream.author==users.get_current_user()):
            status = (1,1)
            for picture in pictures:
                print('index')
                print index
                infos.append((picture.key(),picture.imgkey,index))
                index=index+1
                if(index==4):
                    index = 0
            url=urllib.urlencode({'streamname': stream.name})


        else:
            if(users.get_current_user()):
                count=CountViews.query(CountViews.name==stream.name,ancestor=ndb.Key('User',stream.author_name)).fetch()[0]
                count.numbers=count.numbers+1
                count.totalviews=count.totalviews+1
                count.put()
                status = (1,0)
                for picture in pictures:
                    infos.append((picture.key(),0,index))
                    index=index+1
                    if(index==4):
                        index = 0
            else:
                self.redirect(users.create_login_url(self.request.url))


        template_values={"stream_name": stream_name,"infos":infos,"url":url,"status":status}
        template=JINJA_ENVIRONMENT.get_template("showmore_index.html")
        self.response.write(template.render(template_values))


application = webapp2.WSGIApplication([
    ('/upload', Upload),
    ('/showmore.*', ShowPictures),
    ('/delpic', DeletePictures),
    ('/subscribe', SubscribeStream),
    ('/img.*', Image),
    ('/stream.*', ViewSinglePage),
    ('/uploadurlhandler',UploadUrlHandler)

], debug=True)