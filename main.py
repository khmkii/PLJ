import re
from flask import (abort, Flask, flash, g, render_template, redirect,
                   request, url_for)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (current_user, LoginManager, login_required, logout_user,
                             login_user)

import forms
import models


DEBUG = True
HOST = '0.0.0.0'
PORT = 8000


app = Flask(__name__)
app.secret_key = '87t8g$3574 y425YFv.-45vvy$%VY)%^/y5t3q40'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'


def next_is_valid(next):
    """This will need completing for open redirect protection
    depending on the use of action parameter in html form etc"""
    return True


@login_manager.user_loader
def user_loader(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.before_request
def before_request():
    g.user = current_user
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.JournalForm()
    if form.validate_on_submit():
        with models.DATABASE.transaction():
            models.User.make_user(
                username=form.username.data,
                password=form.password.data
            )
        flash("Journal registered", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash("Username or password does not match", "failure")
        else:
            if check_password_hash(user.password, form.password.data):
                user.authenticated = True
                user.save()
                login_user(user, remember=True)
                next = request.args.get('next')
                if not next_is_valid(next):
                    return abort(400)
                return redirect(url_for('index'))
            else:
                flash("Something does not match", "failure")
    return render_template('login.html', form=form)


@app.route('/list')
@login_required
def index():
    entries = models.Entry.select().where(models.Entry.learner == g.user._get_current_object())
    return render_template('index.html', entries=entries)


@app.route('/new', methods=('GET', 'POST'))
@login_required
def new():
    form = forms.EntryForm()
    if form.validate_on_submit():
        models.Entry.make_entry(
            title=form.title.data,
            date=form.date.data,
            time=form.time.data,
            learned=form.learned.data,
            resources=form.resources.data,
            learner=g.user._get_current_object()
        )
        flash("Entry added", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/detail')
@login_required
def detail():
    entry_title = request.args.get('entry')
    entry = models.Entry.get(models.Entry.title == entry_title)
    resources = entry.resources.split(',')
    return render_template('detail.html', entry=entry, resources=resources)


@app.route('/edit', methods=('GET', 'POST'))
@login_required
def edit():
    edit = forms.EditForm()
    if request.method == 'POST':
        entry_to_edit = models.Entry.get(
            models.Entry.title == request.args.get('entry_title')
        )
        if edit.title.data:
            entry_to_edit.title = edit.title.data
        if edit.date.data:
            entry_to_edit.date = edit.date.data
        if edit.time.data:
            entry_to_edit.time = edit.time.data
        if edit.learned.data:
            entry_to_edit.learned = edit.learned.data
        if edit.resources.data:
            entry_to_edit.resources = edit.resources.data
        entry_to_edit.save()
        return redirect(url_for('index'))
    else:
        return render_template('edit.html', edit=edit)


@app.route('/delete')
@login_required
def delete():
    del_title = request.args.get('entry_title')
    deletion = models.Entry.get(models.Entry.title == del_title)
    deletion.delete_instance()
    flash('Entry deleted', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    models.initialise()
    app.run(debug=DEBUG, host=HOST, port=PORT)
