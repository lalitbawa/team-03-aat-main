from flask import render_template, request, url_for, redirect, flash, jsonify
from AATApp import app, db
from AATApp.models import User, Questions, Assessment, AssessmentQuestions
from AATApp.forms import LoginForm, RegistrationForm, MultipleChoiceForm, ShortAnswerForm, NewAssessment, AddMultipleChoice, AddShortAnswer
from flask_login import login_user, logout_user, current_user


@app.route('/view_all_questions')
def view_all_questions():
    if current_user.is_admin:
        questions = Questions.query.all()
        return render_template('view_all_questions.html', questions=questions)
    else :
        flash('You are not authorized to view this page')
        return redirect(url_for('home'))
    
@app.route('/marks')
def marks():
    if current_user.is_student:
        return render_template('marks.html')
    else :
        flash('Page only accessible to students')
        return redirect(url_for('home'))

@app.route('/view_all_questions/<int:question_id>')
def view_question(question_id):
    question = Questions.query.get_or_404(question_id)
    return render_template('view_question.html', title=question.question, question=question, )


@app.route('/add_multiple_question', methods=['GET', 'POST'])
def add_multiple_question():
    form = AddMultipleChoice()
    if form.validate_on_submit():
        question_data = form.question.data
        choice1 = form.choice1.data
        choice2 = form.choice2.data
        choice3 = form.choice3.data
        choice4 = form.choice4.data
        answer = form.answer.data.replace(" ","").lower()
        feedback = form.feedback.data
        question = Questions(is_multiple_choice=1,
                             question=question_data,
                             choice1=choice1,
                             choice2=choice2,
                             choice3=choice3,
                             choice4=choice4,
                             answer=answer,
                             feedback=feedback,
                             creator_id=current_user.id)
        db.session.add(question)
        db.session.commit()

        flash('Question created!')
        return redirect(url_for('view_all_questions'))
    return render_template('add_multiple_question.html', form=form)


@app.route('/view_all_questions/<int:question_id>/edit_multiple_question',
           endpoint='edit_multiple_question', methods=['GET', 'POST'])
def edit_multiple_question(question_id):
    question = Questions.query.get(question_id)
    form = AddMultipleChoice(obj=question)
    if request.method == 'POST':
        form_data = request.form
        question.is_multiple_choice = True
        question.question = form_data['question']
        question.choice1 = form_data['choice1']
        question.choice2 = form_data['choice2']
        question.choice3 = form_data['choice3']
        question.choice4 = form_data['choice4']
        question.answer = form_data['answer']
        question.feedback = form_data['feedback']
        question.creator_id = current_user.id
        db.session.commit()
        flash('Question saved!')
        return redirect(url_for('view_all_questions'))
    return render_template('edit_multiple_question.html',
                           question=question, form=form)


@app.route('/view_all_questions/<int:question_id>/delete_question',
           methods=['GET', 'POST'])
def delete_question(question_id):
    question = Questions.query.get_or_404(question_id)
    if request.method == 'POST':
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted!')
        return redirect(url_for('view_all_questions'))
    return render_template('delete_question.html', question=question)


@app.route('/add_short_answer_question', methods=['GET', 'POST'])
def add_short_answer_question():
    form = AddShortAnswer()
    if form.validate_on_submit():
        question_data = form.question.data
        answer = form.answer.data
        feedback = form.feedback.data
        question = Questions(is_multiple_choice=0,
                             question=question_data,
                             answer=answer,
                             feedback=feedback,
                             creator_id=current_user.id)
        db.session.add(question)
        db.session.commit()
        flash('Question created!')
        return redirect(url_for('view_all_questions'))
    return render_template('add_short_answer_question.html', form=form)


@app.route('/view_all_questions/<int:question_id>/edit_short_answer_question',
           endpoint='edit_short_answer_question', methods=['GET', 'POST'])
def edit_short_answer_question(question_id):
    question = Questions.query.get(question_id)
    form = AddShortAnswer(obj=question)
    if request.method == 'POST':
        form_data = request.form
        question.is_multiple_choice = False
        question.question = form_data['question']
        question.answer = form_data['answer']
        question.feedback = form_data['feedback']
        question.creator_id = current_user.id
        db.session.commit()
        flash('Question saved!')
        return redirect(url_for('view_all_questions'))
    return render_template('edit_short_answer_question.html',
                           question=question, form=form)

@app.route('/get_all_questions', methods=['GET'])
def get_all_questions():
    if request.method == 'GET':
        questions = Questions.query.all()
        question_list = []
        for question in questions:
            question_dict = {}
            for column in Questions.__table__.columns:
                question_dict[column.name] = getattr(question, column.name)
            question_list.append(question_dict)
        return jsonify(question_list)
