

from google.appengine.api import users

import webapp2
import jinja2
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class LoginPage(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            self.redirect('management')
        else:
            url_linktext = "Log in"
            url = users.create_login_url('/management')

            template_values = {
                'url': url,
                'url_linktext': url_linktext,
            }
            template = JINJA_ENVIRONMENT.get_template('login_index.html')
            self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/', LoginPage),
], debug=True)