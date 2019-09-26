Our Application: Help New Haven

Help New Haven is a website where users (i.e. churches, food banks) can upload information about local opportunities for people to get food, clothes, shelter, and help that may be needed in difficult financial situations. It has a PDF printable form so these locations can distribute in a tangible way the information to those who do not have access to the internet.


## Page Overview

#### Home Page
Through the homepage ("Home" on the top of the website), people can see the different events offered sorted by the most recent events first. This information can be sorted by what type of help the event is being offered (food, clothing, shelter, other) using tabs on the top of the homepage. From the hompage, a person can access the following pages: Map, PDF, Join/Log in. If a person is already logged in, they will also be able to access "Your Events" and "Create Event".

#### Map
The Map page shows the locations of each event as a pin on the map. When the pin is clicked, information about the event is shown.

#### PDF
The PDF page shows each event information in a table that is printable friendly. The print button on the top of the page will automatically bring the user to printing options.

#### Log in
The login page asks the user for their username and password and will show an error if incorrect. If the person does not have an account, they can press "register" and it will bring them to the register page.

#### Register
To register as a new user, a unique username and a password containing at least 9 characters, at least one number, at least one upper case letter, and at least one lower case letter must be inputted. If it does not meet the requirements, an error message will show.

#### Create Event
"Create Event" will only be an option once a user is logged in. An event can be created through filling out a form that asks for the following: Event Name, Service, Event Date, Start Time, End Time, Expiration Date, Repeat Weekly, Address, and Event Description. Once the event is created, the user will be redirected to the "Your Events" page.

#### Your Events
Once logged in, a person can see the events they created through the "Your Events" page. The events are displayed in a table manner. The user will have the opportunity to edit or delete an event. If the edit button is pressed, it will bring you back to the form.

#### Edit Event
An event can be edited. If it is from a repeated event, that event that was pressed to be editted will only be edited, not the other events. If it is an event that was not repeated but then made to repeat, the new events will be created until the expiration date specified.


## How to use our website ##

# Step 0: Set up
Our site runs off of the flask microframework so all files are included and all you need to run is flask run inside the help directory

# Step 1: Register
As a new user you will want to register a new account by going to "Join/Login" and then register as a new user

# Step 2: Create an Event
Now that you are registered you can create a new event at the "Create a New Event" through the form it is automatically added to the front page and saved into the database

# Step 3: Edit or Delete Events
You can edit or delete your events by going to the “Your Events” page and see the options there. When you edit an event you can see all the old data is filled in automatically for you

# Step 4: See Events
You can see the events you and other users made on the main page and in the map and in the pdf