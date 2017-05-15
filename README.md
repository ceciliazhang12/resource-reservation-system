# Resource Reservation System

URL:
Github:

This system has implemented all the functions required.

Something you need to know:

1. This system supports multiple users. User must log in his/her google account to utilize this system.

2. The system only display valid reservations (end-time not passed) in each page.

3. You can enter 0 or more tags when create/edit resource.
	- Please enter in format of "tag1, tag2, tag3".(There are "," and a space between tags)

4. Delete reservation are only supported in landing page.
	- Since all reservations of current user are displayed there.
	
5. Tags of resources are displayed in landing page and search resource result page.
	- You can click the tag to go to a page displaying all resources with this tag.

5. In resource info page, if current user is owner of this resource, he/she will also see a link to edit this resource.
	- Otherwise user will only see a line "You have no permission to edit this resource!" displayed.
	  
6. User can click a link in resource info page to make new reservation.
	- It handles multiple user input errors when specifying start/end time of reservation.
	- Once error happens, an alert message box will be displayed, don not try enter info in current page again.
	- User must return to former page to re-enter info correctly.
	
7. Reservation info are fully displayed at where reservation appears.
	- resource name and user are linked its own info page as required
	
# extra credits
I impelmented extra requirement 1, 2, 5
1 - The resource's number of past reservations is displayed in resource info page.
2 - User can search resources by name.
5 - When reservations are made, an email confirmation would be sent from my email account (yz3847@nyu.edu) to the user.

# code guide
1. All the data model used in the system are listed in models.py

2. main.py lists all requests handlers and functions to implement this system.

3. All html files are in folder `/templates`
  

A few things need to be mentioned here:
1. Since Google App Engine store datetime object even for an column of TimeProperty,
it's tricky to compare the start time of a resource with the start time of a reservation.
There should be a better way to do this, but this app takes the time part of resource datetime and compare it with user input.
