__author__ = 'wen'

import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db
import webapp2
import jinja2
import os
from stream import Stream
from stream import Picture

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import images

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class error(webapp2.RequestHandler):
    def get(self):
        url = users.create_logout_url('/')
        template_values = {
                'url': url
        }
        template = JINJA_ENVIRONMENT.get_template('error_index.html')
        self.response.write(template.render(template_values))


application = webapp2.WSGIApplication([
    ('/error.*', error),
], debug=True)

