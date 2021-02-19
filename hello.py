from flask import Flask, render_template

# from flask_wtf import Flaskform
# from wtforms import StringField,SubmitField
# from wtforms.validators import DataRequired

#  Need to start Flask by...
# 1. start powershell
# 1a. type bash
# 2. type export FLASK_APP=hello.py
# 3. type export FLASK_ENV=development
# 4. type flask run

# Configure GitHub
# $ git config --global push.default matching
# $ git config --global alias.co checkout
# $ git init
# $ git add .
# $ git commit -am 'comment'


# Create a Flask Instance
app = Flask(__name__)

# Create a route decorator
@app.route("/")

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
