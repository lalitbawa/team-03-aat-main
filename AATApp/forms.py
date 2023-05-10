from flask_wtf import FlaskForm
from AATApp import db
from AATApp.models import Questions, User
from wtforms import StringField, PasswordField, SubmitField, RadioField, BooleanField, SelectField, EmailField, HiddenField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Regexp


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Checks if input username already exists; if it does, asks new user to select a new username"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(
                'Username already exists. Please choose a different one.')

    def validate_email(self, email):
        """Checks if input email is already associated to an account; if it does, asks user to log in instead."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(
                'This email address is already associated with an account. Please log in instead.')


class MultipleChoiceForm(FlaskForm):
    form_choices = RadioField('Choose the correct answer:',
                              choices=[('choice1', 'A: '),
                                       ('choice2', 'B: '),
                                       ('choice3', 'C: '),
                                       ('choice4', 'D: ')],
                              validators=[DataRequired()])
    question_number = 0
    aq_id = HiddenField('assessment_question_id')
    submit = SubmitField('Submit')


class ShortAnswerForm(FlaskForm):
    answer = StringField('Answer', validators=[DataRequired()])
    question_number = 0
    aq_id = HiddenField('assessment_question_id')
    submit = SubmitField('Submit')


class NewAssessment(FlaskForm):
    is_summative = BooleanField('Summative Assessment', default=False)
    title = StringField('Assessment Title', validators=[DataRequired()])
    description = StringField('Assessment Description')
    submit = SubmitField('Submit')


class AddShortAnswer(FlaskForm):
    question = StringField('Question:', validators=[DataRequired()])
    answer = StringField('Answer:', validators=[DataRequired()])
    feedback = StringField('Feedback:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddMultipleChoice(FlaskForm):
    question = StringField('Question:', validators=[DataRequired()])
    choice1 = StringField('Choice 1:', validators=[DataRequired()])
    choice2 = StringField('Choice 2:', validators=[DataRequired()])
    choice3 = StringField('Choice 3:', validators=[DataRequired()])
    choice4 = StringField('Choice 4:', validators=[DataRequired()])
    answer = SelectField('Answer:', choices=[
                         'Choice 1', 'Choice 2', 'Choice 3', 'Choice 4'], validators=[DataRequired()])
    feedback = StringField('Feedback:', validators=[DataRequired()])
    submit = SubmitField('Submit')
