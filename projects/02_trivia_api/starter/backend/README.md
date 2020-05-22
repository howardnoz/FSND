# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

REVIEW_COMMENT
This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code. 

Endpoints
GET '/categories'
GET ...
POST ...
DELETE ...

GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
```
{'1' : "Science",
'2' : "Art",
'3' : "Geography",
'4' : "History",
'5' : "Entertainment",
'6' : "Sports"}
```

GET '/questions'
- Fetches all questions (paginated in groups of 10), a dictionary of categories, currently selected category, and total numberr of returned questions
- Request Arguments: Can accept 1 argument 'page', which will display only the questions on that page
- Returns: An object with keys as questions, total_questions, categories, and current_category
- Sample: http://127.0.0.1:5000/questions?page=2
```
{
  "categories": [
    "Science",
    "Art",
    "Geography",
    "History",
    "Entertainment",
    "Sports"
  ],
  "current_category": 1,
  "questions": [
    {
      "answer": "The Palace of Versailles",
      "category": 3,
      "difficulty": 3,
      "id": 14,
      "question": "In which royal palace would you find the Hall of Mirrors?"
    },
    {
      "answer": "Agra",
      "category": 3,
      "difficulty": 2,
      "id": 15,
      "question": "The Taj Mahal is located in which Indian city?"
    }
  ],
  "success": true,
  "total_questions": 10
}
```

GET '/questions/<int:q_id>'
- Fetches questions with id <q_id>
- Request Arguments: None
- Returns: A json object with success message and the question data
- Sample: http://127.0.0.1:5000/questions/5
```
{
  "q": {
    "answer": "Brazil",
    "category": 6,
    "difficulty": 3,
    "id": 10,
    "question": "Which is the only team to play in every soccer World Cup tournament?"  },
  "success": true
}
```

POST '/questions'
- Creates a new questions
- Request Arguments: json object with keys question, answer, difficulty, and category
- Returns: A json object with success message and the new question data
- Sample: http://127.0.0.1:5000/questions
```
{
    'question': {
        'answer': 'James Bond',
        'category': 3,
        'difficulty': 1,
        'id': 24,
        'question': 'Who are you?'
    },
    'success': True
}
```

POST '/questions/search'
- Search for questions including a speficic string
- Request Arguments: json object with key searchTerm
- Returns: A json object with success message and questions/categories data
- Sample: http://127.0.0.1:5000/questions/search
```
{
  "categories": [
    "Science",
    "Art",
    "Geography",
    "History",
    "Entertainment",
    "Sports"
  ],
  "current_category": 1,
  "questions": [
    {
      "answer": "Uruguay",
      "category": 6,
      "difficulty": 4,
      "id": 11,
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }
  ],
  "success": true,
  "total_questions": 1
}
```

GET '/categories/<int:cat_id>/questions'
- Filter questions by category
- Request Arguments: category id as cat_id
- Returns: A json object with questions filtered by category
- Sample: http://127.0.0.1:5000/categories/<int:cat_id>/questions
```
{
  "questions": [
    {
      "answer": "Escher",
      "category": 2,
      "difficulty": 1,
      "id": 16,
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    }
  ],
  "success: True
}
```

POST '/quizzes'
- Get next question based on quiz format
- Request Arguments: previous_questions array of question ids, and selected category as json format ```json {'quiz_category':{'id':<category_id>}} ```
- Returns: a json object including all previous questions and the current questino to display for quiz
- Sample: http://127.0.0.1:5000/quizzes
```
request:
{
    'previous_questions': [16, 17],
    'quiz_category': {'id': 2}
}

return: 
{
  "previous_questions": [
    16,
    17
  ],
  "question": {
    "answer": "Agra",
    "category": 3,
    "difficulty": 2,
    "id": 15,
    "question": "The Taj Mahal is located in which Indian city?"
  },
  "success": true
}
```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
