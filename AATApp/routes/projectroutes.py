from flask import render_template, request, url_for, redirect, flash
from AATApp import app, db
from AATApp.models import User, Questions, Assessment, AssessmentQuestions
from AATApp.forms import LoginForm, RegistrationForm, MultipleChoiceForm, ShortAnswerForm, NewAssessment, AddMultipleChoice
from flask_login import login_user, logout_user, current_user


@app.route("/")
@app.route("/home")
def home():
    assessments = db.session.query(Assessment).all()
    if current_user.is_authenticated:
        return render_template('home.html', assessments=assessments)
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            flash('You\'ve successfully logged in,' +
                  ' ' + current_user.username + '!')
            return redirect(url_for('home'))
        flash('Invalid username or password.')
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data,
                    email=form.email.data, is_student=True)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
    if current_user.is_authenticated:
        return render_template('register.html', title='Register', form=form)
    return redirect(url_for('login'))


@app.route("/logout")
def logout():
    logout_user()
    flash('You\'re now logged out. Thanks for your visit!')
    return redirect(url_for('home'))


@app.route("/test", methods=['GET', 'POST'])
def test_page():
    questions = Questions.query.all()
    forms = {}
    for question in questions:
        if question.is_multiple_choice == True:
            forms['mq' + str(question.id)
                  ] = (MultipleChoiceForm(prefix='mq' + str(question.id)))
        else:
            forms['sa' + str(question.id)
                  ] = (ShortAnswerForm(prefix='sa' + str(question.id)))
    return render_template('test.html', title="Test", forms=forms, questions=questions)


