from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return self.id is None

    def get_id(self):
        return unicode(self.id)

    def check_password(self, candidate):
        return bcrypt.check_password_hash(self.password_hash, candidate)

    def __repr__(self):
        return '<User:%d %r>' % (self.id, self.email)


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(11), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5))
    journey_action = db.Column(db.String(200), nullable=False)
    charge = db.Column(db.String(10))
    credit = db.Column(db.String(10))
    balance = db.Column(db.String(10))
    note = db.Column(db.String(500))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(
        'User',
        backref=db.backref('history', lazy='dynamic'))

    def __init__(self, user, date, start_time, end_time,
                 journey_action, charge, credit, balance, note):
        self.user = user
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.journey_action = journey_action
        self.charge = charge
        self.credit = credit
        self.balance = balance
        self.note = note

    def __repr__(self):
        return '<History %r %r>' % (self.user_id, self.journey_action)

    def __eq__(self, other):
        return all([
            self.date == other.date,
            self.start_time == other.start_time,
            self.journey_action == other.journey_action])
