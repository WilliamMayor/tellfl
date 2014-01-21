import os

from flask import Flask, render_template, request

from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:////Users/william/Desktop/dev.db')
db.init_app(app)


@app.route('/users/')
def users():
    return render_template('users.html', users=User.query.all())


@app.route('/users/<int:uid>/history/')
def user_history(uid):
    return render_template('history.html', history=User.query.get_or_404(uid).history)


@app.route('/history/', methods=['POST'])
def history():
    return str(request.form)
