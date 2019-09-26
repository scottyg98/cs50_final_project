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


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- MAIN EVENT VIEWS -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@app.route("/")
def index():
    """Home Page list of events"""

    # THIS WILL DELETE THE event if its expiration date is the same as today
    today = datetime.datetime.strptime(str(date.today()), '%Y-%m-%d')
    expire = db.execute("DELETE FROM events WHERE expiration=:expiration", expiration=today.strftime('%B %d, %Y'))

    events = db.execute("SELECT * FROM events")

    locations = []
    event_ids = []
    for field in events:
        dateandtime = field["date"] + "<br>" + field["time_start"] + " - " + field["time_end"]
        locations.append([ field["location"], "<b>" + field["name"] + "</b>:<br>" + field["type"]+ "<br>" + dateandtime ])
        event_ids.append([ field["event_id"], field["type"] ])
    events.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%B %d, %Y'))
    return render_template("index.html", events=events, locations=json.dumps(locations), event_ids=json.dumps(event_ids))


@app.route("/map")
def eventmap():
    """makes map"""

    events = db.execute("SELECT * FROM events")



    time = events[0]["date"]
    print("FIRST DATE")
    print(time)
    time = datetime.datetime.strptime(time, '%B %d, %Y')
    date_added = time + datetime.timedelta(7)
    print(time)
    date_added = time + datetime.timedelta(7)
    date_added = 
    print("t DATE")
    print(date_added)

    # time_start_parsed = datetime.datetime.strptime(field["time_start"], '%I:%M %p')
    # field["time_start"] = time_start_parsed.strftime('%H:%M')

    # date_normal = date_normal + datetime.timedelta(7)

    # date=date_normal.strftime('%B %d, %Y'),
    # date_normal = datetime.datetime.strptime(request.form.get("date"), '%Y-%m-%d')



    locations = []
    for field in events:

        dateandtime = field["date"] + "<br>" + field["time_start"] + " - " + field["time_end"]
        locations.append([ field["location"], "<b>" + field["name"] + "</b>:<br>" + field["type"]+ "<br>" + dateandtime ])

    return render_template("map.html", locations=json.dumps(locations))

@app.route("/pdf")
def pdf():
    """ makes into printable friendly table """

    events = db.execute("SELECT * FROM events")
    events.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%B %d, %Y'))

    return render_template("pdf.html", events=events)



#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- USER MANAGEMENT -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

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

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        # Ensure password and confirmation match
        if not request.form.get("password") == request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Encrypt password
        hashpass = generate_password_hash(request.form.get("password"))

        # Register user in database
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                            username=request.form.get("username"),
                            hash=hashpass)
        if not result:
            return apology("Username is not unique", 400)

        # Remember which user has logged in
        session["user_id"] = result

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- USER EVENT ADMINISTRATION -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@app.route("/yourevents", methods=["GET", "POST"])
@login_required
def yourevents():
    """Show event feed of ur events"""

    # get a dict of all the shares th user owns
    events = db.execute("SELECT * FROM events WHERE user_id=:id", id=session["user_id"])
    events.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%B %d, %Y'))

    if request.method == "POST":
        if request.form.get("delete"):
            event_id = request.form.get("delete")
            delete = db.execute( "DELETE FROM events WHERE event_id=:event_id", event_id=event_id )

        elif request.form.get("edit"):
            session["event_id"] = request.form.get("edit")
            return redirect("/editevent")

        else:
            return apology("error", 400)
        return redirect("/yourevents")

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

        location = request.form.get("location_pt_one") + " New Haven, Connecticut"
        date_normal = datetime.datetime.strptime(request.form.get("date"), '%Y-%m-%d')
        expiration_normal = datetime.datetime.strptime(request.form.get("expiration"), '%Y-%m-%d')
        time_normal_start = datetime.datetime.strptime(request.form.get("time_start"), '%H:%M')
        time_normal_end = datetime.datetime.strptime(request.form.get("time_end"), '%H:%M')
        repeat = request.form.get("repeat")

        if repeat == "Yes":
            while date_normal != expiration_normal:
                event = db.execute("INSERT INTO events (type, date, location, shortdescription, name, user_id, expiration, time_start, time_end) VALUES(:type, :date, :location, :shortdescription, :name, :user_id, :expiration, :time_start, :time_end)",
                                    type=request.form.get("type"),
                                    date=date_normal.strftime('%B %d, %Y'),
                                    location=location,
                                    shortdescription=request.form.get("shortdescription"),
                                    name=request.form.get("name"),
                                    user_id=session["user_id"],
                                    expiration=expiration_normal.strftime('%B %d, %Y'),
                                    time_start=time_normal_start.strftime('%I:%M %p'),
                                    time_end=time_normal_end.strftime('%I:%M %p'))
                date_normal =  datetime.datetime.strptime(date_normal, '%Y-%m-%d+7')
        else:
             event = db.execute("INSERT INTO events (type, date, location, shortdescription, name, user_id, expiration, time_start, time_end) VALUES(:type, :date, :location, :shortdescription, :name, :user_id, :expiration, :time_start, :time_end)",
                                    type=request.form.get("type"),
                                    date=date_normal.strftime('%B %d, %Y'),
                                    location=location,
                                    shortdescription=request.form.get("shortdescription"),
                                    name=request.form.get("name"),
                                    user_id=session["user_id"],
                                    expiration=expiration_normal.strftime('%B %d, %Y'),
                                    time_start=time_normal_start.strftime('%I:%M %p'),
                                    time_end=time_normal_end.strftime('%I:%M %p'))

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

        location = request.form.get("location_pt_one") + " New Haven, Connecticut"
        date_normal = datetime.datetime.strptime(request.form.get("date"), '%Y-%m-%d')
        expiration_normal = datetime.datetime.strptime(request.form.get("expiration"), '%Y-%m-%d')
        time_normal_start = datetime.datetime.strptime(request.form.get("time_start"), '%H:%M')
        time_normal_end = datetime.datetime.strptime(request.form.get("time_end"), '%H:%M')

        event = db.execute("UPDATE events SET type=:type, date=:date, location=:location, shortdescription=:shortdescription, name=:name, user_id=:user_id, expiration=:expiration, time_start=:time_start, time_end=:time_end WHERE event_id=:event_id",
                            type=request.form.get("type"),
                            date=date_normal.strftime('%B %d, %Y'),
                            location=location,
                            shortdescription=request.form.get("shortdescription"),
                            name=request.form.get("name"),
                            user_id=session["user_id"],
                            expiration=expiration_normal.strftime('%B %d, %Y'),
                            time_start=time_normal_start.strftime('%I:%M %p'),
                            time_end=time_normal_end.strftime('%I:%M %p'),
                            event_id=event_id)
        # Redirect user to home page
        return redirect("/yourevents")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("editevent.html", event=event)


#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- ERROR HANDLING -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
