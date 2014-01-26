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
    from_ = request.form['sender'].strip('<>')
    print 'From:', from_
    u = User.query.filter_by(email=from_).first()
    print 'User:', u
    if u is not None:
        for f in request.files.values():
            print '  File:', f.name
            if f.filename.endswith('.csv'):
                for h in parse.history(f):
                    h.user = u
                    db.session.add(h)
                db.session.commit()
    return 'OK', 200


@app.route('/users/')
def users():
    return render_template('users.html', users=User.query.all())


@app.route('/users/<int:uid>/history/')
def user_history(uid):
    return render_template(
        'history.html',
        history=User.query.get_or_404(uid).history)
