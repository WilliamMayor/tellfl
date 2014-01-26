import os

from flask import Flask, render_template, request

import parse
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:////Users/william/Desktop/dev.db')
db.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/mailgun/', methods=['POST'])
def mailgun():
    from_ = request.form['from'].strip('<>')
    u = User.query.filter_by(email=from_).first()
    if u is not None:
        for f in request.files:
            for h in parse.csv(f):
                h.user = u
                db.session.add(h)
    return 'OK', 200


@app.route('/users/')
def users():
    return render_template('users.html', users=User.query.all())


@app.route('/users/<int:uid>/history/')
def user_history(uid):
    return render_template(
        'history.html',
        history=User.query.get_or_404(uid).history)
