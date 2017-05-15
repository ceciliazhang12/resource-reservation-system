from google.appengine.ext import ndb

class Resource(ndb.Model):
    # data model for representing a resource
    id = ndb.StringProperty(indexed=True)
    # user email
    owner = ndb.StringProperty()
    name = ndb.StringProperty()
    available_start_time = ndb.DateTimeProperty()
    available_end_time = ndb.DateTimeProperty()
    tags = ndb.StringProperty(repeated=True)
    last_reservation_time = ndb.DateTimeProperty(auto_now_add=True)
    # store the num of how many times it has been reserved in the past
    num_reserved = ndb.IntegerProperty()

class Reservation(ndb.Model):
    # data model for representing a reservation
    id = ndb.StringProperty(indexed=True)
    # user email
    user = ndb.StringProperty()
    resource_id = ndb.StringProperty()
    resource_name = ndb.StringProperty()
    start_time = ndb.DateTimeProperty()
    duration = ndb.IntegerProperty()  # minute
    end_time = ndb.DateTimeProperty()
    reservation_made_time = ndb.DateTimeProperty(auto_now_add=True)


