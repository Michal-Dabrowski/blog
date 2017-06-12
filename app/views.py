from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import blog_app, db, lm
import app
from .forms import LoginForm, RegisterForm, EditForm, PostForm, MessageForm, CompareFiles
from .models import User, Post, Message, Thread
from datetime import datetime
from config import POSTS_PER_PAGE
from werkzeug.utils import secure_filename
from .my_tools import compare_files
import os

@app.blog_app.route('/')
@app.blog_app.route('/index', methods=['GET', 'POST'])
@app.blog_app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    user = g.user
    form = PostForm()
    if form.validate_on_submit():
        body = form.post.data
        timestamp = datetime.utcnow()
        user_id = g.user.id
        add_post(body=body, timestamp=timestamp, user_id=user_id)
        return redirect(url_for('index'))
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html', user=user, posts=posts, form=form)

@app.blog_app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.login.data
        password = form.password.data
        registered_user = User.query.filter_by(nickname=username, password=password).first()
        if registered_user is None:
            flash("Wrong login or password!")
            return redirect('/login')
        else:
            session['remember_me'] = form.remember_me.data
            login_user(registered_user, remember=session['remember_me'])
            return redirect('/index')
    return render_template('login.html',
                           title='Sign In',
                           form=form
                           )

@app.blog_app.route('/register', methods= ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        register_user(form.login.data, form.password.data, form.email.data)
        registered_user = User.query.filter_by(nickname=form.login.data, password=form.password.data).first()
        login_user(registered_user, remember=session['remember_me'])
        return(redirect(url_for('index')))
    return render_template("register.html",
                           title="Register",
                           form=form)

@app.blog_app.route('/logout')
def logout():
    logout_user()
    return redirect('/index')

@app.blog_app.route('/user/<nickname>')
@app.blog_app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User {} not found.'.format(nickname))
        return(redirect(url_for('index')))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           posts=posts)

@app.blog_app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        file = form.avatar.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.blog_app.config['UPLOAD_FOLDER'], filename))
            g.user.avatar = filename
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)

@app.blog_app.route('/send_message/<nickname>', methods=['GET', 'POST'])
@login_required
def send_message(nickname):
    sender = g.user
    receiver = User.query.filter_by(nickname=nickname).first()
    if receiver == None:
        flash('User {} not found.'.format(nickname))
        return redirect(url_for('index'))
    form = MessageForm()
    if form.validate_on_submit():
        body = form.message.data
        timestamp = datetime.utcnow()
        sender_id = sender.id
        thread = sender.get_thread_with(receiver)
        if thread is None:
            thread = Thread()
            receiver.threads.append(thread)
            sender.threads.append(thread)
            db.session.add_all([thread, sender, receiver])
            db.session.commit()
            thread = sender.get_thread_with(receiver)
        message = Message(body=body, timestamp=timestamp, sender_id=sender_id, thread_id=thread.id)
        db.session.add_all([message, sender, receiver])
        db.session.commit()
        flash('Message sent.')
        return redirect(url_for('user', nickname=nickname))
    return render_template('send_message.html', form=form, nickname=nickname)

@app.blog_app.route('/messages')
@login_required
def threads():
    user = User.query.filter_by(nickname=g.user.nickname).first()
    messages = user.my_messages()
    return render_template('threads.html', messages=messages, thread=Thread)


@app.blog_app.route('/messages/<nickname>', methods=['GET', 'POST'])
@login_required
def messages(nickname):
    receiver = User.query.filter_by(nickname=g.user.nickname).first()
    sender = User.query.filter_by(nickname=nickname).first()
    messages = receiver.get_all_messages_with_user(sender)
    form = MessageForm()
    if form.validate_on_submit():
        body = form.message.data
        timestamp = datetime.utcnow()
        sender_id = receiver.id
        thread = receiver.get_thread_with(sender)
        if thread is None:
            thread = Thread()
            receiver.threads.append(thread)
            sender.threads.append(thread)
            db.session.add_all([thread, sender, receiver])
            db.session.commit()
            thread = receiver.get_thread_with(sender)
        message = Message(body=body, timestamp=timestamp, sender_id=sender_id, thread_id=thread.id)
        db.session.add_all([message, sender, receiver])
        db.session.commit()
        flash('Message sent.')
        return redirect(url_for('messages', nickname=sender.nickname))
    return render_template('messages.html', messages=messages, sender=sender, receiver=receiver, form=form)

@app.blog_app.route('/compare_files', methods=['GET', 'POST'])
def compare_files():
    form = CompareFiles()
    if form.validate_on_submit():
        file_1 = form.file_1.data
        file_2 = form.file_2.data
        filename_1 = secure_filename(file_1.name)
        filename_2 = secure_filename(file_2.name)
        if file_1 and file_2 and allowed_file(file_1.filename) and allowed_file(file_2.filename):
            flash("SUCCESS!")
            #compare_files(file_1, file_2)
            return render_template('compare_files.html', form=form)
        return render_template('compare_files.html', form=form)
    return render_template('compare_files.html', form=form)

@app.blog_app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('user', nickname=nickname))

@app.blog_app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))

@blog_app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

def register_user(login, password, email):
    user = User(nickname=login, password=password, email=email)
    db.session.add(user)
    db.session.commit()
    db.session.add(user.follow(user))
    db.session.commit()

@app.blog_app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.blog_app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

def add_post(body, timestamp, user_id):
    post = Post(body=body, timestamp=timestamp, user_id=user_id)
    db.session.add(post)
    db.session.commit()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.blog_app.config['ALLOWED_EXTENSIONS']