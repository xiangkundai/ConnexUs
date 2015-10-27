import cgi
import urllib
import re
import time

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db

import os
import random

import webapp2

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import images
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

from stream import Stream
from stream import Picture
from stream import CountViews
from stream import Count_pic


import jinja2
import json



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

        uploadurl = blobstore.create_upload_url('/upload')
        showmoreurl=urllib.urlencode({'showmore': stream.name+"=="+users.get_current_user().nickname()})
        geoviewurl=urllib.urlencode({'geoview': stream.name+"=="+users.get_current_user().nickname()})
        template_values = {
            'user_name':users.get_current_user().nickname(),
            'showmoreurl': showmoreurl,
            'stream_name': stream_name,
            'pictures':pictures,
            'status':status,
            'uploadurl':uploadurl,
            'geoviewurl': geoviewurl

        }
        template = JINJA_ENVIRONMENT.get_template('viewsinglestream_index.html')
        self.response.write(template.render(template_values))

        #class Image(blobstore_handlers.BlobstoreDownloadHandler):
        #   def get(self):
        #      picture = db.get(self.request.get('img_id'))
        #     blob_info = blobstore.BlobInfo.get(picture.imgkey)
        #   self.send_blob(blob_info)

class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)


class Upload(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        print('1')


        original_url=self.request.headers['Referer']
        img=self.get_uploads()[0]
        stream_name=re.findall('=(.*)',original_url)[0]
        if Stream.author==users.get_current_user():
            stream=Stream.query(Stream.name==stream_name, Stream.author==users.get_current_user()).fetch()[0]
            #for img in imgs:
            print('3')
            picture=Picture(parent=db.Key.from_path('Stream',stream_name),imgkey=str(img.key()))
            stream.lastnewdate= picture.uploaddate
            pic_count= Count_pic.query(ancestor=ndb.Key('Stream',stream_name)).fetch()[0]
            print pic_count
            #  print(pic_counts)
            # for pic_count in pic_counts:
            pic_count.numbers=pic_count.numbers+1
            pic_count.put()

            if stream.tag != None:
                picture.caption = stream.tag[0]

            #stream.numberofpictures=pic_count.numbers
            #stream.total=stream.total+1
            #picture.id=str(stream.total)
            #img=img.resize((300,300))
            # picture.imgkey=str(img.key())
            # print  picture.imgkey
            picture.put()
            stream.put()
            # print('!!')
            #print (stream.numberofpictures)
            #  print (stream.total)
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
            images.delete_serving_url(picture.imgkey)
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
            #stream.subscribers.append(users.get_current_user().nickname())
            stream.subscribers.append(users.get_current_user().email())
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
                url=urllib.urlencode({'streamname': stream.name})
                for picture in pictures:
                    infos.append((picture.key(),picture.imgkey,index))
                    index=index+1
                    if(index==4):
                        index = 0
            else:
                self.redirect(users.create_login_url(self.request.url))


        template_values={"stream_name": stream_name,"infos":infos,"url":url,"status":status,'user_name':users.get_current_user().nickname()}
        template=JINJA_ENVIRONMENT.get_template("showmore_index.html")
        self.response.write(template.render(template_values))

class GeoView(webapp2.RequestHandler):
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
                lat = random.random()
                lng = random.random()
                infos.append((picture.key(),picture.imgkey,picture.uploaddate, lat, lng, index))
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
                url=urllib.urlencode({'streamname': stream.name})
                for picture in pictures:
                    lat = random.random()
                    lng = random.random()
                    infos.append((picture.key(),picture.imgkey,picture.uploaddate, lat, lng,index))
                    index=index+1
                    if(index==4):
                        index = 0
            else:
                self.redirect(users.create_login_url(self.request.url))


        template_values={"stream_name": stream_name,"infos":infos,"url":url,"status":status}
        template=JINJA_ENVIRONMENT.get_template("geoview_index.html")
        self.response.write(template.render(template_values))


class viewSingleStreamFromAndroid(webapp2.RequestHandler):
    def get(self):
        stream_name = self.request.get("stream_name")
        email = self.request.get("email")
        caption = []
        displayImages = []
        #print stream_name
        pictures = db.GqlQuery("SELECT * FROM Picture " +"WHERE ANCESTOR IS :1 "+"ORDER BY uploaddate DESC",db.Key.from_path('Stream',stream_name))
        stream = Stream.query(Stream.name==stream_name).fetch()[0]

        if stream.author_name.lower()!= email.split("@",1)[0]:
            count=CountViews.query(CountViews.name==stream.name,ancestor=ndb.Key('User',stream.author_name)).fetch()[0]
            count.numbers=count.numbers+1
            count.totalviews=count.totalviews+1
            count.put()



        for pic in pictures:
            url = images.get_serving_url(pic.imgkey)
            url = url + "=s500"
            displayImages.append(url)
            caption.append(pic.caption)
            #print url

        dictPassed = {'displayImages':displayImages,'caption':caption,'author':str(stream.author)}
        #dictPassed = {'displayImages':displayImages,'caption':caption}
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)


class GetUploadURL(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/uploadFromAndroid')
        upload_url = str(upload_url)
        dictPassed = {'upload_url':upload_url}
        print(upload_url)
        jsonObj = json.dumps(dictPassed, sort_keys=True,indent=4, separators=(',', ': '))
        self.response.write(jsonObj)


class UploadFromAndroid(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload = self.get_uploads()[0]
        stream_name = self.request.params['stream_name']
        img_location_lat = float(self.request.params['locationLat'])
        img_location_long = float(self.request.params['locationLong'])
        print(img_location_long)
        print(img_location_lat)
        email = self.request.params['email']
        user_photo = Picture(parent=db.Key.from_path('Stream',stream_name),imgkey=str(upload.key()), loc=db.GeoPt(img_location_lat,img_location_long) )
        caption=self.request.params['photoCaption']
        if caption != None:
            user_photo.caption = caption


        print(user_photo.loc)
        user_photo.put()

        stream=Stream.query(Stream.name==stream_name).fetch()[0]
        stream.lastnewdate= user_photo.uploaddate
        pic_count= Count_pic.query(ancestor=ndb.Key('Stream',stream_name)).fetch()[0]

        #  print(pic_counts)
        # for pic_count in pic_counts:
        pic_count.numbers=pic_count.numbers+1
        pic_count.put()
        #print (stream)
        #print (pic_count.numbers)
        #print (stream.numberofpictures)
        #print (stream.total)
        #stream.numberofpictures=pic_count.numbers
        #stream.total=stream.total+1
        #picture.id=str(stream.total)
        #img=img.resize((300,300))
        # picture.imgkey=str(img.key())
        # print  picture.imgkey
       # picture.put()
        stream.put()



application = webapp2.WSGIApplication([
    ('/upload', Upload),
    ('/showmore.*', ShowPictures),
    ('/geoview.*', GeoView),
    ('/delpic', DeletePictures),
    ('/subscribe', SubscribeStream),
    ('/view_photo/([^/]+)?',ViewPhotoHandler),
    ('/stream.*', ViewSinglePage),
    ('/uploadurlhandler',UploadUrlHandler),
    ('/viewSingleStream',viewSingleStreamFromAndroid),
    ('/getUploadURL',GetUploadURL),
    ('/uploadFromAndroid',UploadFromAndroid)

], debug=True)