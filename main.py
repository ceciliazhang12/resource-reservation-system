#!/usr/bin/env python

# Copyright 2016 Google Inc.
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

# [START imports]
import os
from datetime import datetime, time, timedelta
import uuid
import time as t

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail

import jinja2
import webapp2

from models import Resource, Reservation
from __builtin__ import True

PATH_TEMPLATE = os.path.join(os.path.dirname(__file__), 'templates')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(PATH_TEMPLATE),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

# Helper Function
def send_mail(resource, reservation):
    text = "Hi,\n\n" + "You've reserved {0} from {1} to {2}. " \
               .format(reservation.resource_name, reservation.start_time,
                       reservation.end_time)
    mail.send_mail(sender="yz3847@nyu.edu", to=reservation.user,
                   subject="Reservation Confirmend.", body=text)


'''
Landing Page, which displays the following 4 sections:
  user login / logout link
  reservations made for resources by that user (sorted by the reservation time)
  all resources in the system (shown in reverse time order based on last made reservation)
  resources owned by that user
  a link to create a new resource
'''
class LandingPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
            # retrieve reservations by current user
            now_time = datetime.now() - timedelta(minutes=300)
            reservation_by_curr_user = Reservation.query(ndb.AND(Reservation.user == user.email(),
                                                                 Reservation.end_time > now_time)) \
                                                  .fetch()
            if reservation_by_curr_user:
                reservation_by_curr_user = sorted(reservation_by_curr_user, key=lambda r: r.start_time)

            # retrieve all resources in system
            sorted_resources = Resource.query().order(-Resource.last_reservation_time)
            # retrieve resources owned by current user
            resources_owned = Resource.query(Resource.owner==user.email())

            template_values = {
                'user': user,
                'reservation_by_curr_user': reservation_by_curr_user,
                'sorted_resources': sorted_resources,
                'resources_owned': resources_owned,
                'url': url,
                'url_linktext': url_linktext,
            }

            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))

        else:
            self.redirect(users.create_login_url(self.request.uri))
            # url_linktext = 'Login'

'''
  CreateResource Handler enables the function of creating a new resource
'''
class CreateResource(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('newResource.html')
        template_values = {}
        self.response.write(template.render(template_values))

    def post(self):
        resource = Resource()
        user = users.get_current_user()
        if user:
            resource.owner = user.email()
            resource.id = str(uuid.uuid4())
            resource.name = self.request.get('name')
            start_time = map(int, self.request.get('available_start_time').split(':'))
            end_time = map(int, self.request.get('available_end_time').split(':'))
            resource.available_start_time = datetime.combine(datetime.today(), time(*start_time))
            resource.available_end_time = datetime.combine(datetime.today(), time(*end_time))
            resource.tags = self.request.get('tags').split(', ')
            resource.num_reserved = 0
            resource.put()
            t.sleep(0.1)
        self.redirect('/')
 
'''
  ViewResource Handler handels displaying the main page for an existing resource
'''        
class ViewResource(webapp2.RequestHandler):
    def get(self):
        resource_id = self.request.get('id')
        owner = Resource.query(Resource.id == resource_id).get().owner
        count = Resource.query(Resource.id == resource_id).get().num_reserved
        curr_user = users.get_current_user()
        now_time = datetime.now() - timedelta(minutes=300)

        reservations = Reservation.query(ndb.AND(Reservation.resource_id == resource_id,
                                                 Reservation.end_time >= now_time)).fetch()
        reservations = sorted(reservations, key=lambda r: r.start_time)
        
        # currentUser = str(users.get_current_user().email())
        template_values = {
            'reservations': reservations,
            'curr_user': curr_user,
            'owner': owner,
            'resource_id': resource_id,
            'count':count,
        }
        template = JINJA_ENVIRONMENT.get_template('resource.html')
        self.response.write(template.render(template_values))  

'''
  ViewResource Handler handels the function of editing an existing resource
''' 
class EditResource(webapp2.RequestHandler):
    def get(self):
        resource_id = self.request.get('id')
        resource = Resource.query(Resource.id == resource_id).get()
        start = resource.available_start_time
        end = resource.available_end_time
        template_values = {
            'id': resource_id,
            'name': resource.name,
            'available_start_time': start,
            'available_end_time': end,
            'tags': ', '.join(resource.tags),
        }
        template = JINJA_ENVIRONMENT.get_template('editResource.html')
        self.response.write(template.render(template_values))

    def post(self):
        resource_id = self.request.get('id')
        resource = Resource.query(Resource.id == resource_id).get()
        resource.name = self.request.get('name')
#         today = datetime.now().date()
        start_time = map(int, self.request.get('available_start_time').split(':'))
        end_time = map(int, self.request.get('available_end_time').split(':'))
        resource.available_start_time = datetime.combine(datetime.today(), time(*start_time))
        resource.available_end_time = datetime.combine(datetime.today(), time(*end_time))
        resource.tags = self.request.get('tags').split(', ')
        resource.put()
        t.sleep(0.1)
        self.redirect('/')

'''
  ViewUser Handler handels displaying the main page for an user
'''  
class ViewUser(webapp2.RequestHandler):     
    def get(self):
        user_email = self.request.get('email')
        # retrieve user's reservations 
        reservation_by_curr_user = Reservation.query(Reservation.user == user_email)
        if reservation_by_curr_user:
            reservation_by_curr_user = reservation_by_curr_user.order(Reservation.start_time)
        
        # retrieve resources owned by this user
        resources_owned = Resource.query(Resource.owner==user_email)

        template_values = {
            'reservation_by_curr_user': reservation_by_curr_user,
            'resources_owned': resources_owned,
        }
        template = JINJA_ENVIRONMENT.get_template('user.html')
        self.response.write(template.render(template_values))        

'''
  CreateResservation Handler enables the function of creating a new reservation
'''
class CreateReservation(webapp2.RequestHandler):
    def get(self):
        resource_id = self.request.get('id')
        resource = Resource.query(Resource.id == resource_id).get()
        template_values = {
            'id': resource_id,
            'name': resource.name
        }
        template = JINJA_ENVIRONMENT.get_template('newReservation.html')
        self.response.write(template.render(template_values))

    def post(self):
        resource_id = self.request.get('id')
        resource_name = self.request.get('name')
        start_time = time(*map(int, self.request.get('available_start_time').split(':')))
        start_time = datetime.combine(datetime.today(), start_time)
        duration = int(self.request.get('duration'))
        resource = Resource.query(Resource.id == resource_id).get()
        end_time = start_time + timedelta(minutes=duration)
        # check time format and availability
        has_error = False
        msg = ''
        
        # error check
        if end_time < start_time:
            has_error = True
            msg = 'Error, wrong format of start time or duration. Please return to former page to enter correctly.'
    
        elif resource.available_start_time > start_time or \
            resource.available_end_time < end_time:
            has_error = True
            msg = 'Error, resource not available during the selected period. Please return to former page to enter another time period.'

        else:
            reservations = Reservation.query(Reservation.resource_id == resource_id).fetch()
            for r in reservations:
                if not (end_time <= r.start_time or start_time >= r.end_time):
                    has_error = True
                    msg = 'Error, reservation conflict. Please return to former page to enter another time period.'
        
        if has_error:
            template = JINJA_ENVIRONMENT.get_template('newReservation.html')
            template_values = {'msg': msg}
            self.response.write(template.render(template_values))
            
        else:
            # add reservation if no error
            reservation = Reservation()
            reservation.id = str(uuid.uuid4())
            reservation.user = str(users.get_current_user().email())
            reservation.start_time = start_time
            reservation.duration = duration
            reservation.end_time = end_time
            reservation.resource_id = resource_id
            reservation.resource_name = resource_name
            reservation.put()
            resource.last_reservation_time = datetime.now() - timedelta(minutes=300)
            resource.num_reserved += 1
            resource.put()
            t.sleep(1)

            send_mail(resource, reservation)

            self.redirect('/') 
            
'''
  CreateResservation Handler enables the function of 
  generating a RSS link for an existing reservation
'''           
class GenerateRSS(webapp2.RequestHandler):
    def get(self):
        resource_id = self.request.get('id')
        resource = Resource.query(Resource.id == resource_id).get()
        reservations = Reservation.query(Reservation.resource_id == resource_id).fetch()
         
        header = '<?xml version="1.0" encoding="UTF-8" ?>'
        tag_owner = '<owner>{}</owner>'.format(resource.owner)
        tag_name = '<name>{}</name>'.format(resource.name)
        tag_start = '<start_time>{}</start_time>'.format(resource.available_start_time)
        tag_end = '<end_time>{}</end_time>'.format(resource.available_end_time)
        tags_reservation = []
        for r in reservations:
            t = {}
            t['user'] = '<reservedBy>{}</reservedBy>'.format(r.user)
            t['start'] = '<reservedAt>{}</reservedAt>'.format(r.start_time)
            tags_reservation.append(t)
            
        template_values = {
            'header': header,
            'owner': tag_owner,
            'name': tag_name,
            'start_time': tag_start,
            'end_time': tag_end,
            'reservations': tags_reservation,
        }
        template = JINJA_ENVIRONMENT.get_template('rss.html')
        self.response.write(template.render(template_values))    

'''
  DeleteResservation Handler enables deleting an existing reservation in Landing Page
'''
class DeleteReservation(webapp2.RequestHandler):
    def post(self):
        reservation_id = self.request.get('reservation_id')
        reservation = Reservation.query(Reservation.id == reservation_id).get()
        reservation.key.delete()
        t.sleep(0.1)
        self.redirect('/')

'''
  ResourceBy Handler enables the function of filtering existing resources by tag
'''        
class ResourcesByTag(webapp2.RequestHandler):
    def get(self):
        tag = self.request.get('tag').lower()
        resources = Resource.query().order(-Resource.last_reservation_time).fetch()
        filtered_resources = []
        for r in resources:
            tags = [t.lower().strip() for t in r.tags]
            if tag in tags:
                filtered_resources.append(r)

        template_values = {
            'tag': tag,
            'resources': filtered_resources,
        }
        template = JINJA_ENVIRONMENT.get_template('tag.html')
        self.response.write(template.render(template_values))
        
'''
  SearchResource Handler enables the function of searching existing resources by name
'''         
class SearchResource(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('searchResource.html')
        self.response.write(template.render(template_values))         
        
    def post(self):
        name = self.request.get('name').lower()
        resources = Resource.query().order(-Resource.last_reservation_time).fetch()
        results = []
        for r in resources:
            resource_name = r.name.strip().lower()
            if name in resource_name:
                results.append(r)
        print resources
        template_values = {
            'name': name,
            'resources': results,
        }
        template = JINJA_ENVIRONMENT.get_template('searchResource.html')
        self.response.write(template.render(template_values))  

# [START app]
app = webapp2.WSGIApplication([
    ('/', LandingPage),
    ('/newResource.html', CreateResource),
    ('/resource.html', ViewResource),
    ('/editResource.html', EditResource),
    ('/newReservation.html', CreateReservation),
    ('/user.html', ViewUser),
    ('/index.html', DeleteReservation),
    ('/tag.html', ResourcesByTag),
    ('/rss.html', GenerateRSS),
    ('/searchResource.html', SearchResource),
    ], debug=True)
# [END app]
