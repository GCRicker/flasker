from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#  Need to start Flask by...
# 1. start powershell
# 1a. type bash
# 2. type "export FLASK_APP=hello.py"
# 3. type "export FLASK_ENV=development"
# 4. type "flask run"
# 5. type password below
# CSS changes use cntrl F5 for new cache

# Configure GitHub
# $ git config --global push.default matching
# $ git config --global alias.co checkout
# $ git init
# $ git add .
# $ git commit -am 'comment'

#
# Create a Flask Instance
app = Flask(__name__)

# Add Database

# Using sqlite...
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

# Using mySQL
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://Greg:Zaq1qaz1@HAGRID/users"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://Greg:mysql@Weasley/users"

# Secret Key
app.config["SECRET_KEY"] = "My secret key for csrf used to protect forms"

# Initialize the Database
db = SQLAlchemy(app)


# Create a database Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a String
    def __repr__(self):
        return "<Name %r>" % self.name


# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Update Database Record
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":  # figure out where its coming from...
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template(
                "update.html", form=form, name_to_update=name_to_update
            )
        except:
            flash("Error!  Looks like there was a problem")
            return render_template(
                "update.html", form=form, name_to_update=name_to_update
            )
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update)


# def index():
#     return "<h1>Hello World!</h1>"

#                Jinja Filters
# safe - Will not allow HTML to be passed in for security
# capitalize - Capitalize first letter
# lower - All letters lower
# upper - All letters upper
# title - Capitalize first letter of every word
# trim - Remove trailing spaces
# striptags - Remove any tags that are trying to be passed


@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.email.data = ""
        flash("User Added Successfully!")

    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)


# Create a route decorator
@app.route("/")
def index():
    first_name = "Gregory"
    stuff = "This is <strong>BOLD</strong> Text"

    favorite_pizza = ["Pepperoni", "cheese", "mushrooms", 41]
    return render_template(
        "index.html", first_name=first_name, stuff=stuff, favorite_pizza=favorite_pizza
    )


# localhost:5000/user/Greg
# in the URL, what you put in <name> will forward


@app.route("/user/<name>")
def user(name):
    # Use Jinja2 to use Python Pass in a variable
    return render_template("user.html", user_name=name)


# Create Custom Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def server_bad(e):
    return render_template("500.html"), 500


# Create Name Page
@app.route("/name", methods=["GET", "POST"])
def name():
    name = None  # First time it will be none until form is filled out
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""  # Clear it out for the next form use
        flash("Form Submitted Successfully")
    return render_template("name.html", name=name, form=form)
