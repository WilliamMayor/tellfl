from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.email


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
    user = db.relationship('User', backref=db.backref('history', lazy='dynamic'))

    def __init__(self, user, date, start_time, end_time, journey_action, charge, credit, balance, note):
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


if __name__ == '__main__':
    u = User('mail@williammayor.co.uk')
    h = History(u, '29-Nov-2013', '06:00', '07:00', 'Ruislip to Euston Square', '5.00', None, '18.75', '')
    db.session.add(u)
    db.session.add(h)
    db.session.commit()
