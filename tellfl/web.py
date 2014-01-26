import os

from flask.ext.login import (
    login_user, login_required,
    logout_user, current_user)
from flask import Flask, render_template, request, redirect, url_for

import parse
from models import db, User
from login import login_manager, LoginForm

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:////Users/william/Desktop/dev.db')
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    'development key')
db.init_app(app)
login_manager.init_app(app)


@app.route('/')
def index():
    if current_user.is_authenticated():
        return redirect(url_for('history'))
    return redirect(url_for('login'))


@app.route('/mailgun/', methods=['POST'])
def mailgun():
    from_ = request.form['sender'].strip('<>')
    u = User.query.filter_by(email=from_).first()
    if u is not None:
        for f in request.files.values():
            if f.filename.endswith('.csv'):
                for h in parse.history(f):
                    h.user = u
                    db.session.add(h)
                db.session.commit()
    return 'OK', 200


@app.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        return redirect(request.args.get("next") or url_for("index"))
    return render_template("login.html", form=form)


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/history/')
@login_required
def history():
    return render_template(
        'history.html',
        history=current_user.history)
