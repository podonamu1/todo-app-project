from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, DateField, TimeField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange


class UserCreateForm(FlaskForm):
    id = StringField('id', validators=[DataRequired(), Length(min=4, max=20)])
    name = StringField('name', validators=[DataRequired(), Length(min=2, max=100)])
    password1 = PasswordField('password1', validators=[
        DataRequired(), Length(min=4, max=30),
        EqualTo('password2', '비밀번호가 일치하지 않습니다.')
    ])
    password2 = PasswordField('password2', validators=[DataRequired()])


class UserModifyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=2, max=100)])
    info = TextAreaField('info')


class LoginForm(FlaskForm):
    id = StringField('id', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class TodoForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=2, max=100)])
    date = DateField('date')
    time = TimeField('time')
    info = TextAreaField('info')


class DetailForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(min=2, max=100)])
    progress = FloatField('progress', validators=[NumberRange(min=0.0, max=100.0)])


class CommentForm(FlaskForm):
    text = TextAreaField('text', validators=[DataRequired()])
