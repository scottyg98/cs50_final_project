"""--------------------------------------------------------------------------------"""
"""    _    _      _         _   _                 _    _                          """
"""   | |  | |    | |       | \ | |               | |  | |                         """
"""   | |__| | ___| |_ __   |  \| | _____      __ | |__| | __ ___   _____ _ __     """
"""   |  __  |/ _ \ | '_ \  | . ` |/ _ \ \ /\ / / |  __  |/ _` \ \ / / _ \ '_ \    """
"""   | |  | |  __/ | |_) | | |\  |  __/\ V  V /  | |  | | (_| |\ V /  __/ | | |   """
"""   |_|  |_|\___|_| .__/  |_| \_|\___| \_/\_/   |_|  |_|\__,_| \_/ \___|_| |_|   """
"""                 | |                                                            """
"""                 |_|                                                            """
"""--------------------------------------------------------------------------------"""

import os
import json
import datetime
import re

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///helpNH.db")


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- MAIN EVENT VIEWS -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@app.route("/")
def index():
    """Home Page list of events"""

    events = db.execute("SELECT * FROM events")

    # THIS WILL DELETE THE event if its expiration date is the same as today
    today = datetime.datetime.strptime(str(date.today()), '%Y-%m-%d')

    # initializes an empty array of all dates and their ids
    all_dates = []
    all_dates_ids = []

    # loops through every event in events
    # checks to make sure that event_date does not equal todays date, if it does it deletes the event from the database
    for event in events:
        event_date = datetime.datetime.strptime(event["expiration"], '%B %d, %Y')
        if event_date <= today:
            expire = db.execute("DELETE FROM events WHERE event_id=:event_id", event_id=event["event_id"])

    # initializes an empty array of locations and event ids
    locations = []
    event_ids = []

    # loops through every every field in events
    # sets dateandtime equal to the event fields date + time_state + time_end
    # appends to locations array the location, name, type, and dateandtime
    # appends to event_ids the event_id and type
    for field in events:
        dateandtime = field["date"] + "<br>" + field["time_start"] + " - " + field["time_end"]
        locations.append([field["location"], "<b>" + field["name"] + "</b>:<br>" + field["type"] + "<br>" + dateandtime])
        event_ids.append([field["event_id"], field["type"]])

    # sorts the events by date (most recent)
    events.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%B %d, %Y'))

    # renders index.html with the information of the events
    return render_template("index.html", events=events, locations=json.dumps(locations), event_ids=json.dumps(event_ids))


@app.route("/map")
def eventmap():
    """makes map"""

    # get a dict of all events from the database
    events = db.execute("SELECT * FROM events")

    # intializes an empty array named locations
    locations = []

    # loops through every fields in events
    # sets dateandtime equal to the event fields date + time_state + time_end
    # appends to locations array the location, name, type, and dateandtime
    for field in events:
        dateandtime = field["date"] + "<br>" + field["time_start"] + " - " + field["time_end"]
        locations.append([field["location"], "<b>" + field["name"] + "</b>:<br>" + field["type"] + "<br>" + dateandtime])

    # renders map.html with the map information from the events
    return render_template("map.html", locations=json.dumps(locations))


@app.route("/pdf")
def pdf():
    """ makes into printable friendly table """

    # selects all events from the database
    events = db.execute("SELECT * FROM events")

    # sorts the events by date
    events.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%B %d, %Y'))

    # renders pdf.html with event information (a table with all the event information)
    return render_template("pdf.html", events=events)


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- USER MANAGEMENT -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # sets username, password, and confirmation as variable names for the form values in register.html
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # validates the password by length, uppercase, lowercase, and number inclusion
        if (len(password) < 8):
            return apology("password must be greater than 8 characters", 400)
        elif not re.search("[a-z]", password):
            return apology("password must include a lowercase letter!", 400)
        elif not re.search("[A-Z]", password):
            return apology("password must include an uppercase letter!", 400)
        elif not re.search("[0-9]", password):
            return apology("Password must include a number!", 400)

        # Ensure confirmation password was submitted
        if not confirmation:
            return apology("must provide confirmation", 400)

        # Ensure password and confirmation match
        elif not password == confirmation:
            return apology("passwords do not match", 400)

        # Encrypt password
        hashpass = generate_password_hash(request.form.get("password"))

        # Register user in database
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                            username=username,
                            hash=hashpass)
        if not result:
            return apology("username is not unique", 400)

        # Remember which user has logged in
        session["user_id"] = result

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- USER EVENT ADMINISTRATION -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@app.route("/yourevents", methods=["GET", "POST"])
@login_required
def yourevents():
    """Show event feed of ur events"""

    # get a dict of all the shares the user owns
    events = db.execute("SELECT * FROM events WHERE user_id=:id", id=session["user_id"])

    # sorts the events in the dict by date
    events.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%B %d, %Y'))

    # if it is a post method
    if request.method == "POST":

        # if delete is submitted, delete the event from the database
        if request.form.get("delete"):
            event_id = request.form.get("delete")
            delete = db.execute("DELETE FROM events WHERE event_id=:event_id", event_id=event_id)

        # if edit is submitted, redirect to /editevent
        elif request.form.get("edit"):
            session["event_id"] = request.form.get("edit")
            return redirect("/editevent")

        else:
            return apology("error", 400)

        # redirect to /yourevents
        return redirect("/yourevents")

    # render yourevents.html with event information
    return render_template("yourevents.html", events=events)


@app.route("/eventcreate", methods=["GET", "POST"])
@login_required
def eventcreate():
    """CREATE NEW EVENTS"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # makes sure every form was filled out
        for info in request.form:
            if not request.form.get(info):
                message = "must provide " + info
                return apology(message, 400)

        # setting variables equal to the fields from eventcreate.html
        location = request.form.get("location_pt_one") + " New Haven, Connecticut"
        date_normal = datetime.datetime.strptime(request.form.get("date"), '%Y-%m-%d')
        expiration_normal = datetime.datetime.strptime(request.form.get("expiration"), '%Y-%m-%d')
        time_normal_start = datetime.datetime.strptime(request.form.get("time_start"), '%H:%M')
        time_normal_end = datetime.datetime.strptime(request.form.get("time_end"), '%H:%M')
        repeat = request.form.get("repeat")

        # if the event repeats, insert event into the database with a repetition
        if repeat == "Yes":
            print("Repeat")
            while date_normal <= expiration_normal:
                event = db.execute("INSERT INTO events (type, date, location, shortdescription, name, user_id, expiration, time_start, time_end, repeat) VALUES(:type, :date, :location, :shortdescription, :name, :user_id, :expiration, :time_start, :time_end, :repeat)",
                                   type=request.form.get("type"),
                                   date=date_normal.strftime('%B %d, %Y'),
                                   location=location,
                                   shortdescription=request.form.get("shortdescription"),
                                   name=request.form.get("name"),
                                   user_id=session["user_id"],
                                   expiration=expiration_normal.strftime('%B %d, %Y'),
                                   time_start=time_normal_start.strftime('%I:%M %p'),
                                   time_end=time_normal_end.strftime('%I:%M %p'),
                                   repeat=repeat)
                date_normal = date_normal + datetime.timedelta(7)

        # else, insert the event into the database once
        else:
            event = db.execute("INSERT INTO events (type, date, location, shortdescription, name, user_id, expiration, time_start, time_end, repeat) VALUES(:type, :date, :location, :shortdescription, :name, :user_id, :expiration, :time_start, :time_end, :repeat)",
                               type=request.form.get("type"),
                               date=date_normal.strftime('%B %d, %Y'),
                               location=location,
                               shortdescription=request.form.get("shortdescription"),
                               name=request.form.get("name"),
                               user_id=session["user_id"],
                               expiration=expiration_normal.strftime('%B %d, %Y'),
                               time_start=time_normal_start.strftime('%I:%M %p'),
                               time_end=time_normal_end.strftime('%I:%M %p'),
                               repeat=repeat)

        # Redirect user to home page
        return redirect("/yourevents")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("eventcreate.html")


@app.route("/editevent", methods=["GET", "POST"])
@login_required
def editevent():
    """edits ur evnet"""
    event_id = session["event_id"]
    # get a dict of all the shares th user owns
    event = db.execute("SELECT * FROM events WHERE event_id=:event_id", event_id=event_id)
    for field in event:
        # parse date
        date_parsed = datetime.datetime.strptime(field["date"], '%B %d, %Y')
        field["date"] = date_parsed.strftime('%Y-%m-%d')
        # parse exp date
        expiration_parsed = datetime.datetime.strptime(field["expiration"], '%B %d, %Y')
        field["expiration"] = expiration_parsed.strftime('%Y-%m-%d')
        # parse time
        time_start_parsed = datetime.datetime.strptime(field["time_start"], '%I:%M %p')
        field["time_start"] = time_start_parsed.strftime('%H:%M')

        time_end_parsed = datetime.datetime.strptime(field["time_end"], '%I:%M %p')
        field["time_end"] = time_end_parsed.strftime('%H:%M')

        # remove new haven, ct from lcoation
        field["location"] = field["location"][:-23]

    if request.method == "POST":

        # makes sure every form was filled out
        for info in request.form:
            if not request.form.get(info):
                message = "must provide " + info
                return apology(message, 400)

        # setting variables equal to the fields from eventcreate.html
        location = request.form.get("location_pt_one") + " New Haven, Connecticut"
        date_normal = datetime.datetime.strptime(request.form.get("date"), '%Y-%m-%d')
        expiration_normal = datetime.datetime.strptime(request.form.get("expiration"), '%Y-%m-%d')
        time_normal_start = datetime.datetime.strptime(request.form.get("time_start"), '%H:%M')
        time_normal_end = datetime.datetime.strptime(request.form.get("time_end"), '%H:%M')
        repeat = request.form.get("repeat")

        # updates database event
        event = db.execute("UPDATE events SET type=:type, date=:date, location=:location, shortdescription=:shortdescription, name=:name, user_id=:user_id, expiration=:expiration, time_start=:time_start, time_end=:time_end, repeat=:repeat WHERE event_id=:event_id",
                           type=request.form.get("type"),
                           date=date_normal.strftime('%B %d, %Y'),
                           location=location,
                           shortdescription=request.form.get("shortdescription"),
                           name=request.form.get("name"),
                           user_id=session["user_id"],
                           expiration=expiration_normal.strftime('%B %d, %Y'),
                           time_start=time_normal_start.strftime('%I:%M %p'),
                           time_end=time_normal_end.strftime('%I:%M %p'),
                           event_id=event_id,
                           repeat=repeat)

        # if the event repeats, add it in again a week later (timedelta(7))
        if repeat == "Yes":
            date_normal = date_normal + datetime.timedelta(7)
            while date_normal <= expiration_normal:
                # adds event into database
                event = db.execute("INSERT INTO events (type, date, location, shortdescription, name, user_id, expiration, time_start, time_end, repeat) VALUES(:type, :date, :location, :shortdescription, :name, :user_id, :expiration, :time_start, :time_end, :repeat)",
                                   type=request.form.get("type"),
                                   date=date_normal.strftime('%B %d, %Y'),
                                   location=location,
                                   shortdescription=request.form.get("shortdescription"),
                                   name=request.form.get("name"),
                                   user_id=session["user_id"],
                                   expiration=expiration_normal.strftime('%B %d, %Y'),
                                   time_start=time_normal_start.strftime('%I:%M %p'),
                                   time_end=time_normal_end.strftime('%I:%M %p'),
                                   repeat=repeat)
                date_normal = date_normal + datetime.timedelta(7)

        # Redirect user to home page
        return redirect("/yourevents")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("editevent.html", event=event)


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- ERROR HANDLING -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
