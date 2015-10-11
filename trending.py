import cgi
import urllib
import re

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db
from google.appengine.api import mail

import webapp2

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import images
from google.appengine.api import urlfetch

from stream import Stream
from stream import Picture
from stream import Global
from stream import CountViews

import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Trending(webapp2.RequestHandler):
    def get(self):

        gl=Global.query(Global.name=="global").fetch()
        stream_list = []
        count_list = []
        if len(gl)>0:
            gl=gl[0]
        #streams=Stream.query(Stream.author==users.get_current_user()).order(-Stream.views).fetch(3)
        counts=CountViews.query().order(-CountViews.numbers).fetch(3)

        for count in counts:
            stream=Stream.query(Stream.name==count.name).fetch()
            if (len(stream)>0):
                stream = stream[0]
                stream_list.append(stream)
                count_list.append(count.numbers)


        gl=Global.query(Global.name=="global").fetch()
        str = ""
        if(len(gl)>0):
            gl=gl[0]
            fre=gl.limit
            if fre==0:
                str="No reports"
            if fre==1:
                str="Every 5 Minutes"
            if fre==12:
                str="Every 1 hour"
            if fre==288:
                str="Every day"

        print count_list
        print stream_list
        template_values = {
                        'str':str,
                        'count_list':count_list,
                        'stream_list': stream_list
                     }
        template = JINJA_ENVIRONMENT.get_template('trending_index.html')
        self.response.write(template.render(template_values))

class Update(webapp2.RequestHandler):
    def post(self):
        original_url=self.request.headers['Referer']
        frequency=self.request.get("frequency")
        gl=Global.query(Global.name=="global").fetch()
        #self.response.write(gl)
        if len(gl)<=0:
            gl=Global(name="global",count=0,limit=0)
        else:
            gl=gl[0]

        self.response.write(frequency)
        if frequency=="no":
            gl.limit=0
        if frequency=="5m":
            gl.limit=1  # in times of increasement of cron schedule
        if frequency=="1h":
            gl.limit=12
        if frequency=="1d":
            gl.limit=288
        #self.response.write(gl)
        gl.put()
        self.redirect(original_url)

class Task(webapp2.RequestHandler):
    def get(self):
        #if users.get_current_user():
        gl=Global.query(Global.name=="global").fetch()
        #self.response.write(gl) # test
        if(len(gl)>0):
            gl=gl[0]
            gl.count=gl.count+1
            #self.response.write(gl.count) # test
            if(gl.count==gl.limit): #Change!# instead of ==
                gl.count=0
                # if users.get_current_user():
                default_context = "Stream Trending Updated\n\n"
                emailSubject = "Stream Trending"
                emailSender = "info@mini1-test1.appspotmail.com"
                mail.send_mail(sender = emailSender, to = emailSender, subject = emailSubject, body = default_context)
                mail.send_mail(sender = emailSender, to = "nima.dini@utexas.edu", subject = emailSubject, body = default_context)
                mail.send_mail(sender = emailSender, to = "kevzsolo@gmail.com", subject = emailSubject, body = default_context)
                gl.put()

class Clean(webapp2.RequestHandler):
    def get(self):
        #if users.get_current_user():
        counts=CountViews.query().fetch()
        for count in counts:
            count.numbers=0
            count.put()

application = webapp2.WSGIApplication([
    ('/trending', Trending),
    ('/update', Update),
    ('/task', Task),
    ('/clean', Clean),
], debug=True)