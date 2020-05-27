import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  # CORS(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers 
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  #@cross_origin()
  def get_categories():
    categories = Category.query.all()

    if len(categories) == 0:
        abort(404)
    
    formatted_categories = {}
    for cat in categories:
        formatted_categories[getattr(cat, 'id')]= getattr(cat, 'type')

    return jsonify({
        'success':True,
        'categories': formatted_categories
    });

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10

    questions= Question.query.all()
    formatted_questions = [q.format() for q in questions]
    page_questions = formatted_questions[start:end]
    if (len(page_questions) == 0):
        abort(404)

    categories = Category.query.all()
    if len(categories) == 0:
        abort(404)
    formatted_categories = {}
    for cat in categories:
        formatted_categories[getattr(cat, 'id')]= getattr(cat, 'type')

    return jsonify({
        'success':True,
        'questions': page_questions,
        'total_questions': len(page_questions),
        'categories': formatted_categories,
        'current_category': 1
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:q_id>', methods=['GET'])
  def get_q(q_id):
    q= Question.query.filter_by(id=q_id).one_or_none()

    if q is None:
        abort(404)

    formatted_q= q.format()
    return jsonify({ 'success': True, 'q': formatted_q})

  @app.route('/questions/<int:q_id>', methods=['DELETE'])
  def delete_q(q_id):
    try:
        q= Question.query.filter_by(id=q_id).one_or_none()
        formatted_q= q.format()
        q.delete()
        return jsonify({ 'success': True, 'q': formatted_q})
    except:
        abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_q():
    try:
        content = request.get_json()
        question_text = content['question']
        answer = content['answer']
        difficulty = content['difficulty']
        category= content['category']
        q = Question(question=question_text, answer=answer, difficulty=difficulty, category=category)
        q.insert()
        return jsonify({ 'success': True, 'question': q.format()})
    except:
        abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_q():
    try:
        content = request.get_json()
        searchTerm= content['searchTerm']
        searchTerm= '%'+searchTerm+'%'
        questions = Question.query.filter(Question.question.ilike(searchTerm))
        formatted_questions = [q.format() for q in questions]
        categories = Category.query.all()
        formatted_categories = [cat.format() for cat in categories]
        return jsonify({
            'success':True,
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'categories': formatted_categories,
            'current_category': 1
        })
    except:
        abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def get_q_by_cat(cat_id):
    try:
        cat_id = cat_id
        questions= Question.query.filter(Question.category == cat_id).all()
        formatted_questions = [q.format() for q in questions]
        return jsonify({
            'success':True,
            'questions': formatted_questions,
        });
    except:
        abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_quiz():
    try:
        content = request.get_json()

        previous_questions = content['previous_questions']
        quiz_category_id = int(content['quiz_category']['id']);

        if quiz_category_id == 0:
            questions = Question.query.filter_by(category=quiz_category_id)
        else
            questions = Question.query

        possible_questions = questions.filter(Question.id.notin_(previous_questions)).all()
        if len(previous_questions) == len(questions.all()):
            print('game over')
            return jsonify({
                'success': True,
                'question': None
            }), 200
        question = random.choice(possible_questions).format()
        return jsonify({
            'success': True,
            'question': question,
            'previous_questions': previous_questions,
        }), 200
    except:
        abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request."
      }), 400

  @app.errorhandler(404)
  def resource_not_found(error):
      return jsonify({
        "success": False,
        "error": 404,
        "message": "We're sorry. Resource was not found."
      }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
      return jsonify({
        "success": False,
        "error": 405,
        "message": "We're sorry. Method is not allowed."
      }), 405

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        "success": False,
        "error": 422,
        "message": "We're sorry. The request was understood but unable to be processed."
      }), 422

  return app
