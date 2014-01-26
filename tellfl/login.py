from flask.ext.login import LoginManager
from flask.ext.wtf import Form
from wtforms import (TextField, PasswordField, SubmitField, validators)

from models import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


class LoginForm(Form):
    email = TextField(
        'Email',
        [validators.Required('Please enter your email address.'),
         validators.Email('Please enter your email address.')])
    password = PasswordField(
        'Password',
        [validators.Required('Please enter a password.')])
    submit = SubmitField('Login')

    def validate(self):
        if not Form.validate(self):
            return False

        self.user = User.query.filter_by(email=self.email.data.lower()).first()
        if self.user and self.user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append('Invalid email or password')
        return False
