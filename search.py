import cgi
import urllib
import re
import os
import sys
import os.path

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db

import webapp2



from google.appengine.api import images
from google.appengine.api import urlfetch

from stream import Stream
from stream import Picture

import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class searchView(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('search_index.html')
        self.response.write(template.render())


class showSearch(webapp2.RequestHandler):
    def get(self):
        url = self.request.url
        stream_name = re.findall('searchStream=(\S+)',url)
        if len(stream_name) == 0:
            self.response.write(url)
        else:
            stream_name = re.findall('searchStream=(\S+)',url)[0]
            streams = Stream.query().fetch()
            nameList = list()
            key_list = []
            stream_list = []
            for stream in streams:
                nameList.append(stream.name)

            index = list()
            for i in xrange(len(nameList)):
                index.append(LCS(nameList[i], stream_name))
            tmp = zip(index, nameList)
            tmp.sort(reverse = True)
            #we only show five most relation streams
            if len(tmp) < 5:
                showNum = len(tmp)
            else:
                showNum = 5





            for i in xrange(showNum):
                stream = Stream.query(Stream.name==tmp[i][1]).fetch()[0]
                stream_list.append(stream)
                #self.response.write(stream.numberofpictures)
                if stream.numberofpictures > 0:
                    pictures=db.GqlQuery("SELECT * FROM Picture " +"WHERE ANCESTOR IS :1 "+"ORDER BY uploaddate DESC",db.Key.from_path('Stream',stream.name))
                    key_list.append(pictures[0].key())

                else:
                    key_list.append(0)


            template_values = {
                        'showNum': showNum,
                        'stream_name': stream_name,
                        'key_list':key_list,
                        'stream_list': stream_list
                     }
            template = JINJA_ENVIRONMENT.get_template('showsearch_index.html')
            self.response.write(template.render(template_values))

def LCS(stringa, stringb):
    x = list()
    y = list()
    for  i in xrange(len(stringa)):
        x.append(stringa[i])
    for j in xrange(len(stringb)):
        y.append(stringb[j])
    if (len(x) == 0 or len(y) == 0):
        return 0
    else:
        a = x[0]
        b = y[0]
        if (a == b):
            return LCS(x[1:], y[1:])+1
        else:
            return cxMax( LCS(x[1:], y), LCS(x, y[1:] )  )

def cxMax(a, b):
    if (a>=b):
        return a
    else:
        return b

application = webapp2.WSGIApplication([
    ('/search', searchView),
    ('/showsearch', showSearch),
], debug=True)