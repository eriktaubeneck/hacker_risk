from flask.ext.wtf import Form
from flask.ext.wtf.html5 import URLField
from wtforms import TextField, SelectMultipleField

class UserForm(Form):
    username = TextField("Username")
    base_url = URLField("AI URL")

class StartGameForm(Form):
    players = SelectMultipleField("Select Players")
