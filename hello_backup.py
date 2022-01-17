from flask import Flask, render_template, flash, request, redirect, url_for
from flask.helpers import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


#  Need to start Flask by...
# 0. Start mySQL
# 0a.  Start venv
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
migrate = Migrate(app, db)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Create Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful!!!")
                return redirect(url_for("dashboard"))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That User Doesn't Exist!  Try Again!")
    return render_template("login.html", form=form)


# Create Logout function
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You've been logged out!!!   Bye!")
    return redirect(url_for("login"))


# Create Dashboard Page
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = UserForm()

    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":  # figure out where its coming from...
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        name_to_update.username = request.form["username"]
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)
        except:
            flash("Error!  Looks like there was a problem")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)

    return render_template("dashboard.html")


# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))  # used to designate numbers with a variable in web address


# Create a Posts Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Add Post Page
@app.route("/add-post", methods=["GET", "POST"])
# @login_required  First way to restrict access
# 2nd way if from html...
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        # Clear the form by set the fields back to empty on return
        form.title.data = ""
        form.content.data = ""
        form.author.data = ""
        form.slug.data = ""

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        # Return a message
        flash("Blog Post Submitted Successfully!")

    # Redirect to the webpage
    return render_template("add_post.html", form=form)


# Read all Posts Page
@app.route("/posts")
def posts():
    # Grab all the posts from the database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)  # pass to the url the variable posts


# Delete Post
@app.route("/posts/delete/<int:id>")  # include post id to delete
def delete_post(id):  # include post id to delete
    post_to_delete = Posts.query.get_or_404(id)  # Query database for that post
    try:
        db.session.delete(post_to_delete)  # Delete the post
        db.session.commit()  # Alsways have to commit
        flash("Blog Post Was Deleted!")  # Return message it was deleted
        # return to page with all the posts
        posts = Posts.query.order_by(Posts.date_posted)  # Need to retrieve all the posts again to display
        return render_template("posts.html", posts=posts)  # Render page
    except:
        flash("Whoops!  There was a problem deleting the post. Please try again...")  # Error message
        # return to page with all the posts
        posts = Posts.query.order_by(Posts.date_posted)  # Need to retrieve all the posts again to display
        return render_template("posts.html", posts=posts)  # Render page


@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)


@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # update database
        db.session.add(post)  # Add everything in post listed above
        db.session.commit()
        flash("Post has been updated successfully!!")
        return redirect(url_for("post", id=post.id))

    # Fill in the form
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template("edit_post.html", form=form)


#  Practice returning JSON
@app.route("/date")
def get_current_date():
    return {"Date": date.today()}  # Flask will JSONify dictionaries for you


# Create a database Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # Password Stuff
    password_hash = db.Column(db.String(128))

    # Getter Setter for the password  since we only want the hash as the password
    @property  # Turns the function below to allow password to be accessed by ".password", not a function call
    def password(self):  # Getter
        raise AttributeError("password is not a readable attribute!")  # don't return anything

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)  # Note the attribute is not "password"

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a String
    def __repr__(self):
        return "<Name %r>" % self.name


# Create a Name Form Class
class NamerForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Password Test Form Class
class PasswordForm(FlaskForm):
    email = StringField("What is your Email?", validators=[DataRequired()])
    password_hash = PasswordField("What is your Password?", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a User Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField(
        "Password", validators=[DataRequired(), EqualTo("password_hash2")]
    )  # , message='Passwords Must Match!'])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Update Database Record
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":  # figure out where its coming from...
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        name_to_update.username = request.form["username"]
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template("update.html", form=form, name_to_update=name_to_update)
        except:
            flash("Error!  Looks like there was a problem")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)


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
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(
                username=form.username.data,
                name=form.name.data,
                email=form.email.data,
                favorite_color=form.favorite_color.data,
                password_hash=hashed_pw,
            )
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.favorite_color.data = ""
        form.password_hash.data = ""
        flash("User Added Successfully!")

    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)


# Create a route decorator
@app.route("/")
def index():
    first_name = "Gregory"
    stuff = "This is <strong>BOLD</strong> Text"

    favorite_pizza = ["Pepperoni", "cheese", "mushrooms", 41]
    return render_template("index.html", first_name=first_name, stuff=stuff, favorite_pizza=favorite_pizza)


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


# Create password test Page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    email = None  # First time it will be none until form is filled out
    password = None
    pw_to_check = None
    passed = None

    form = PasswordForm()
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ""  # Clear it out for the next form use
        form.password_hash.data = ""  # Clear it out for the next form use
        pw_to_check = Users.query.filter_by(email=email).first()  # Lookup User by Email Address

        # check hashed password
        passed = check_password_hash(pw_to_check.password_hash, password)

    # Pass variables onto the page
    return render_template(
        "test_pw.html", email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form
    )


# Delete User from database
@app.route("/delete/<int:id>")  # pass in users id for lookup and then delete
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    # our_users, name, and form are needed to return to the page
    our_users = Users.query.order_by(Users.date_added)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!")
        # return the page to return to after the delete
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
    except:
        flash("Whoops!  There was a problem deleting the record.")
        return render_template("add_user.html", form=form, name=name, our_users=our_users)
