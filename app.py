"""Authentication application."""

from flask import Flask, redirect, render_template, flash, session
from models import db, connect_db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm
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

# with app.app_context():  
    # Drop all tables when changes are made
    # db.drop_all()
    # Create all tables
    # db.create_all()

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
        flash(f'Welcome {new_user.username}', "success")
        return redirect(f'/users/{new_user.username}')
    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm();
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            flash(f'Welcome back {user.username}', "success")
            session['user'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username or password']
        
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def user(username):
    if 'user' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    else:
        user = User.query.get_or_404(username)
        feedback = Feedback.query.all()
        return render_template('user.html', user=user, feedback=feedback)

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'user' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    else:
        form = FeedbackForm();
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            new_post = Feedback(title=title, content=content, username=username)
            db.session.add(new_post)
            db.session.commit()
            flash('Feedback added', 'success')
            return redirect(f'/users/{username}')
        return render_template('feedback-form.html', form=form, username=username)
    
@app.route('/feedback/<int:feed_id>/update', methods=['GET', 'POST'])
def edit_feedback(feed_id):
    if 'user' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    else:
        this_feedback = Feedback.query.get_or_404(feed_id)
        form = FeedbackForm(obj=this_feedback);
        if form.validate_on_submit():
            this_feedback.title = form.title.data
            this_feedback.content = form.content.data
            db.session.commit()
            flash('Feedback updated', 'success')
            return redirect(f'/users/{this_feedback.username}')
        return render_template('feedback-form.html', form=form)

@app.route("/logout")
def logout():
    session.pop("user")
    return redirect("/")

@app.route('/users/<username>/delete')
def del_user(username):
    if 'user' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    else:
        this_user = User.query.get_or_404(username)
        db.session.delete(this_user)
        db.session.commit()
        flash("User deleted", "success")
        return redirect('/register')
    
@app.route('/feedback/<int:feed_id>/delete')
def del_feedback(feed_id):
    if 'user' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    else:
        this_feedback = Feedback.query.get_or_404(feed_id)
        db.session.delete(this_feedback)
        db.session.commit()
        flash("Feedback deleted", "success")
        return redirect(f'/users/{this_feedback.username}')