"""Authentication application."""

from flask import Flask, redirect, render_template, flash, session
from models import db, connect_db, User
from forms import UserForm, LoginForm
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "secretkey"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)

@app.route("/")
def home():
   return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register():
    form = UserForm();
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username already taken. Please enter a new username')
            form.email.errors.append('Email address already in use. Please enter a new email address')
            return render_template('register.html', form=form)
        session['user'] = new_user.username
        flash(f'Welcome {new_user.username}')
        return redirect('/secret')
    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm();
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            flash(f'Welcome back {user.username}')
            session['user'] = user.username
            return redirect('/secret')
        else:
            form.username.errors = ['Invalid username or password']
        
    return render_template('login.html', form=form)

@app.route('/secret')
def secret():
    if "user" not in session:
        flash("You must be logged in to view!")
        return redirect("/")
    else:
        return 'You made it!'

@app.route("/logout")
def logout():

    session.pop("user")

    return redirect("/")