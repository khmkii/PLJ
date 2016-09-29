from flask_wtf import Form
from wtforms import StringField, PasswordField, DateField,IntegerField, TextAreaField
from wtforms.validators import (DataRequired, Regexp, ValidationError,
                                EqualTo, Length)

from models import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('Cant do it, someone has a journal under that name already')


class JournalForm(Form):
    username = StringField(
        label='Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message="One word, letters, numbers,"
                        "and underscores only"
            ),
            name_exists
        ]
    )
    password = PasswordField(
        label='Password',
        validators=[
            DataRequired(),
            EqualTo('PasswordC', message='Passwords must match'),
            Length(min=8)
        ]
    )
    PasswordC = PasswordField(
        label='Confirm Password',
        validators=[
            DataRequired()
        ]
    )


class LoginForm(Form):
    username = StringField(
        label='Username'
    )
    password = StringField(
        label='Password'
    )


class EntryForm(Form):
    title = StringField(
        label='Title',
        validators=[
            DataRequired(),
        ]
    )
    date = DateField(
        label='Date',
        validators=[
            DataRequired(),
        ]
    )
    time = IntegerField(
        label='Time Spent',
        validators=[
            DataRequired()
        ]
    )
    learned = TextAreaField(
        label='What I Learned',
        validators=[
            DataRequired()
        ]
    )
    resources = TextAreaField(
        label='Resources to Remember',
        validators=[
            DataRequired()
        ]
    )


class EditForm(Form):
    title = StringField(
        label='Title',
    )
    date = DateField(
        label='Date',
    )
    time = IntegerField(
        label='Time Spent',
    )
    learned = TextAreaField(
        label='What I Learned',
    )
    resources = TextAreaField(
        label='Resources to Remember',
    )
