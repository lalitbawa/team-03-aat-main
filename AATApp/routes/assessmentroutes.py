from flask import render_template, request, url_for, redirect, flash, jsonify
from AATApp import app, db
from AATApp.models import Questions, Assessment, AssessmentQuestions, Results, User
from AATApp.forms import MultipleChoiceForm, ShortAnswerForm, NewAssessment
from flask_login import current_user


@app.route('/marks',methods=['GET'])
def get_assessment_results():
    assessments = Assessment.query.all()
    results = []
    for assessment in assessments:
        assessment_questions = AssessmentQuestions.query.filter_by(
            assessment_id=assessment.id).all()
        assessment_results = {
            'assessment': assessment.title,
            'students': {}
        }
        for a_question in assessment_questions:
            question = Questions.query.get(a_question.question_id)
            question_results = Results.query.filter_by(
                a_question_id=a_question.id).all()
            for result in question_results:
                student = User.query.get(result.student_id)
                student_id = student.id
                attempt_number = result.attempt_number
                answer = result.answer
                if student_id in assessment_results['students']:
                    student_results = assessment_results['students'][student_id]
                else:
                    student_results = {
                        'name': student.username,
                        'results': {}
                    }
                if attempt_number in student_results['results']:
                    attempt_results = student_results['results'][attempt_number]

                else:
                    attempt_results = {
                        'correct': 0,
                        'incorrect': 0,
                        'results': []
                    }

                if question.is_multiple_choice:
                    correct_answer = getattr(question, question.answer)
                else:
                    correct_answer = question.answer

                if answer == correct_answer:
                    attempt_results['correct'] += 1
                else:
                    attempt_results['incorrect'] += 1
                attempt_results['results'].append(answer)
                student_results['results'][attempt_number] = attempt_results
                assessment_results['students'][student_id] = student_results
        results.append(assessment_results)
    def get_correct_answers_by_student(data):
      results = {}
      for item in data:
        assessment_name = item['assessment']
        for student_id, student_data in item['students'].items():
            student_name = student_data['name']
            for attempt_num, attempt_data in student_data['results'].items():
                total_correct = attempt_data['correct']
                total_questions = attempt_data['correct'] + attempt_data['incorrect']
                if student_name not in results:
                    results[student_name] = {}
                if assessment_name not in results[student_name]:
                    results[student_name][assessment_name] = {}
                results[student_name][assessment_name][attempt_num] = {
                    'correct': total_correct,
                    'total': total_questions
                }
      return results
    if current_user.is_authenticated:
      return render_template('marks.html', results=get_correct_answers_by_student(results))
    flash('You must be logged in to view this page.')
    return redirect(url_for('login'))
       



@app.route("/assessments", methods=['GET'])
def view_assessments():
  list_assessments = db.session.query(Assessment).all()

  if current_user.is_authenticated and current_user.is_admin:
     list_assessments = db.session.query(Assessment).filter_by(creator_id = current_user.id)

  assessments = []
  if current_user.is_authenticated:
    for assessment in list_assessments:
      aq = db.session.query(AssessmentQuestions).filter_by(assessment_id=assessment.id).first()
      assessment_dict = {
        'assessment': assessment,
        'attempts': db.session.query(Results).filter_by(a_question_id=aq.id, student_id=current_user.id).count()
      }
      assessments.append(assessment_dict)

  if current_user.is_authenticated:
    return render_template('view_assessments.html', assessments=assessments)
  flash('You must be logged in to view this page.')
  return redirect(url_for('login'))

@app.route("/create/assessment", methods=['GET', 'POST'])
def add_assessment():
  form = NewAssessment()

  if form.submit.data and form.validate_on_submit:
    questions = request.form.getlist('question')
    if len(questions) == 0:
      flash('Error: Assessment must contain at least one question')
    else:
      assessment = Assessment(is_summative = form.is_summative.data, title = form.title.data, description = form.description.data, creator_id = current_user.id)
      db.session.add(assessment)
      db.session.commit()
      for i, q in enumerate(questions):
        question = AssessmentQuestions(assessment_id = assessment.id, question_id = int(q), question_number = i + 1)
        db.session.add(question)
        db.session.commit()
      flash('Assessment Created!')
      redirect(url_for('view_assessments'))

  if current_user.is_authenticated:
    if current_user.is_admin:
      return render_template('add_assessment.html', title="Create New Assessment", form=form)
    flash('You must be a course leader to access this page. Please contact the administrator if you believe this is an error.')
    return redirect(url_for('home'))
  return redirect(url_for('login'))

@app.route('/assessment/<int:assessment_id>', methods=['GET', 'POST'])
def assessment(assessment_id):
  assessment = Assessment.query.get_or_404(assessment_id)
  assessment_questions = AssessmentQuestions.query.filter_by(assessment_id=assessment.id).all()
  questions = []
  for q in assessment_questions:
    question_query = Questions.query.get_or_404(q.question_id)
    questions.append(question_query)
  
  mqforms = {}
  saforms = {}

  for question in questions:
    aq = AssessmentQuestions.query.filter_by(assessment_id=assessment.id, question_id=question.id).first()
    aq_id = aq.id
    if question.is_multiple_choice:
        mqforms['mq' + str(question.id)] = MultipleChoiceForm(prefix=f'mq{question.id}', aq_id=aq_id)
    else:
        saforms['sa' + str(question.id)] = ShortAnswerForm(prefix=f'sa{question.id}', aq_id=aq_id)

  # get last question in assessment
  last_q = questions[-1]
  if last_q.is_multiple_choice:
    last_form = mqforms['mq' + str(last_q.id)]
  else:
    last_form = saforms['sa' + str(last_q.id)]
  
  if last_form.submit.data and last_form.validate_on_submit():
      for form_name, form in mqforms.items():
          if form.validate_on_submit():
              aq = AssessmentQuestions.query.filter_by(id = form.aq_id.data).first()
              student_id = current_user.id
              attempts = len(Results.query.filter_by(a_question_id=form.aq_id.data, student_id=student_id).all())
              print(f'Response to {form_name}, assessment_question_id={aq.id} is {form.form_choices.data}')
              result = Results(student_id=student_id,
                                a_question_id = aq.id,
                                answer=form.form_choices.data,
                                attempt_number = attempts + 1)
              db.session.add(result)
              db.session.commit()
      for form_name, form in saforms.items():
          if form.validate_on_submit():
              aq = AssessmentQuestions.query.filter_by(id = form.aq_id.data).first()
              student_id = current_user.id
              attempts = len(Results.query.filter_by(a_question_id=form.aq_id.data, student_id=student_id).all())
              print(f'Response to {form_name}, assessment_question_id={aq.id} is {form.answer.data}')
              result = Results(student_id=student_id,
                                a_question_id=aq.id,
                                answer=form.answer.data,
                                attempt_number = attempts + 1)
              db.session.add(result)
              db.session.commit()
      flash('Assessment Results Saved')
      return redirect(url_for('view_results', assessment_id=assessment.id, attempt_no = attempts + 1))

  if current_user.is_authenticated:
    return render_template('assessment.html', 
                          title=assessment.title, 
                          assessment=assessment, 
                          questions=questions,
                          mqforms=mqforms, 
                          saforms=saforms,
                          last_form=last_form)
  flash('You must be logged in to view this page.')
  return redirect(url_for('login'))

@app.route('/assessment/edit/<int:assessment_id>', methods=['GET', 'POST'])
def edit_assessment(assessment_id):
  assessment = Assessment.query.get(assessment_id)

  # get existing questions in assessment
  assessment_questions = AssessmentQuestions.query.filter_by(assessment_id=assessment.id).all()
  questions = []
  for q in assessment_questions:
    questions.append(Questions.query.filter_by(id=q.question_id).first())

  form = NewAssessment(obj=assessment)

  if form.submit.data and form.validate_on_submit:

    new_questions = request.form.getlist('question')
    # flash error if no questions in assessment
    if len(new_questions) == 0:
      flash('Error: Assessment must contain at least one question')
    else:
      # get all questions and delete them
      old_questions = AssessmentQuestions.query.filter_by(assessment_id=assessment.id).all()
      for q in old_questions:
        db.session.delete(q)
      # add new questions
      assessment.is_summative = form.is_summative.data
      assessment.title = form.title.data
      assessment.description = form.description.data
      assessment.creator_id = current_user.id
      db.session.commit()
      for i, q in enumerate(new_questions):
        question = AssessmentQuestions(assessment_id = assessment.id, question_id = int(q), question_number = i + 1)
        db.session.add(question)
        db.session.commit()
      flash('Assessment Modified!')
      return redirect(url_for('view_assessments'))

  # validate user is a lecturer
  if current_user.is_authenticated:
    if current_user.is_admin:
      return render_template('edit_assessment.html', assessment=assessment, form=form, questions=questions)
    flash('You must be a course leader to access this page. Please contact the administrator if you believe this is an error.')
    return redirect(url_for('home'))
  return redirect(url_for('login'))

@app.route('/assessment/delete/<int:assessment_id>', methods=['GET','POST'])
def delete_assessment(assessment_id):
  assessment = Assessment.query.get_or_404(assessment_id)
  assessment_questions = AssessmentQuestions.query.filter_by(assessment_id=assessment_id).all()
  if request.method == 'POST':
      for q in assessment_questions:
        db.session.delete(q)
      db.session.delete(assessment)
      db.session.commit()
      flash('Assessment deleted!')
      return redirect(url_for('view_assessments'))
  
  if current_user.is_authenticated and current_user.is_admin:
    return render_template('delete_assessment.html', assessment=assessment)
  else:
    flash('You must be an administrator to delete assessments!')
    return redirect(url_for('home'))

@app.route('/results/<int:assessment_id>/<int:attempt_no>')
def view_results(assessment_id, attempt_no):
    # Get assessment, attempt number, and results for given attempt
    assessment = Assessment.query.get_or_404(assessment_id)
    attempt = attempt_no
    assessment_questions = AssessmentQuestions.query.filter_by(assessment_id=assessment.id).all()
    questions = []
    for q in assessment_questions:
      question_query = Questions.query.get_or_404(q.question_id)
      questions.append(question_query)
    
    mqforms = {}
    saforms = {}

    score = 0

    for question in questions:
      aq = AssessmentQuestions.query.filter_by(assessment_id=assessment.id, question_id=question.id).first()
      aq_id = aq.id
      result = Results.query.filter_by(a_question_id=aq.id, attempt_number=attempt, student_id=current_user.id).first()
      if question.is_multiple_choice:
          mqforms['mq' + str(question.id)] = MultipleChoiceForm(prefix=f'mq{question.id}', aq_id=aq_id)
          mqforms[str(question.id) + 'result'] = result.answer
      else:
          saforms['sa' + str(question.id)] = ShortAnswerForm(prefix=f'sa{question.id}', aq_id=aq_id)
          saforms[str(question.id) + 'result'] = result.answer
      if result.answer == question.answer:
         score += 1
  
    if current_user.is_authenticated and current_user.is_student:
      return render_template('view_results.html',
                           title=assessment.title, 
                           assessment=assessment, 
                           questions=questions,
                           mqforms=mqforms, 
                           saforms=saforms,
                           attempt=attempt,
                           score=score)
    else:
       flash('You must be logged in as a student to access this page.')
       return redirect(url_for('home'))