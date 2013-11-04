#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
import md5

classurl = "http://www.csupomona.edu/~tvnguyen7/class/cs245f13/projs/"

class EmailSubscriber(db.Model):
    address = db.EmailProperty()

class PageContent(db.Model):
    md5hash = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

def sendNotifyEmail(userEmail):
    mail.send_mail(sender="CS245 HW Notify <bt.mozoby@gmail.com>",
              to=userEmail,
              subject="Cs245 Auto-Notify",
              body="A change has been made in the CS 245 Projects folder. \n http://www.csupomona.edu/~tvnguyen7/class/cs245f13/projs/ \n You are receiving this email because you subscribed to be emailed updates to the CS245 projects folder. \nScript by Bryan Thornbury. Code Available at http://github.com/mozoby/CS245Notify")

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('<html><body>Subscribe to updates in CS245 Website<br /><form action="/subscribe" method="POST">Email Address: <input type="text" name="email"/><input type="submit"/></form></body></html>')

class Subscribe(webapp2.RequestHandler):
    def post(self):
        email = self.request.get('email')
        self.response.write("<html><body>")
        try:
            subscriber = EmailSubscriber(address=email)
            subscriber.put()
            self.response.write("Successfully added email: " + email)
        except Exception:
            self.response.write("Error adding email")

        self.response.write("</body></html>")

class Notify(webapp2.RequestHandler):
    def get(self):
        #fetch page
        import urllib
        page = urllib.urlopen(classurl)
        #get md5 of page content
        hashcode = md5.new()
        hashcode.update(page.read())
        hashstr = hashcode.hexdigest()
        #compare against previous 
        lastMd5 = PageContent.all().order('-created')
        changed = True
        for r in lastMd5:
            if r.md5hash == hashstr:
                changed = False
            break
       
        #if changed store new md5 and notify all email subscribers
        if changed:
            newMd5 = PageContent(md5hash = hashstr).put()
            for e in EmailSubscriber.all():
                sendNotifyEmail(e.address)

        self.response.write('<html><body>Emailed: ' + str(changed) + '</body></html>')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/subscribe', Subscribe),
    ('/tasks/notify', Notify)
], debug=True)
