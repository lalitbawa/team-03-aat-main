from datetime import datetime
from AATApp import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    hashed_password = db.Column(db.String(128))
    question = db.relationship('Questions', backref='user', lazy=True)
    is_student = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    @property
    def password(self):
        raise AttributeError('Password is not readable.')

    @password.setter
    def password(self, password):
        salt = password + self.username
        self.hashed_password = generate_password_hash(salt)

    def verify_password(self, password):
        salt = password + self.username
        return check_password_hash(self.hashed_password, salt)

    def get_id(self):
        return self.id


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    is_multiple_choice = db.Column(db.Boolean, default=False, nullable=False)
    question = db.Column(db.Integer, nullable=False)
    """
  If the question is short answer (is_multiple_choice = False), all four
  choices should be left empty and "answer" should contain the expected
  answer. If the question is multiple choice (is_multiple_choice = True), all
  four choices should be filled in and "answer" should contain the name of the
  column which contains the correct answer (e.g. "choice3").
  """
    choice1 = db.Column(db.Text)
    choice2 = db.Column(db.Text)
    choice3 = db.Column(db.Text)
    choice4 = db.Column(db.Text)
    answer = db.Column(db.Text, nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    creator_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    is_summative = db.Column(db.Boolean, default=False)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    creator_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)


class AssessmentQuestions(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    question_number = db.Column(db.Integer)


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    student_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    a_question_id = db.Column(db.Integer, db.ForeignKey(
        'assessment_questions.id'), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    attempt_number = db.Column(db.Integer, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
