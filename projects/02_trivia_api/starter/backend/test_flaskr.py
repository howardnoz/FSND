import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_questions(self):
        """Test Questions """
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    def test_404_if_page_invalid(self):
        """Test if 404 is returned when page does not exist"""
        res = self.client().get('/questions\?page\=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_categories(self):
        """Test categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_question(self):
        """Test individual question"""
        res = self.client().get('/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['q'])

    def test_question_deletion(self):
        """Test individual question deletion"""
        res = self.client().get('/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['q'])
        
        res_d = self.client().delete('/questions/2')
        data_d = json.loads(res_d.data)

        self.assertEqual(res_d.status_code, 200)
        self.assertTrue(data_d['success'])
        self.assertTrue(data_d['q'])

        res_g = self.client().get('/questions/2')
        data_g = json.loads(res_g.data)

        self.assertEqual(res_g.status_code, 404)
        self.assertFalse(data_g['success'])
        self.assertTrue(data_g['message'])


    def test_if_404_for_nonexisting_question_deletion(self):
        """Test if 404 returns when attempting deletion of nonexisting question"""
        res = self.client().delete('/question/2000')
        self.assertEqual(res.status_code, 404)

    def test_question_creation(self):
        """Test individual question creation"""
        new_q= {
            'question':'Who are you?',
            'answer': 'James Bond',
            'difficulty': 1,
            'category': 3
        }
        res = self.client().post('/questions', json=new_q)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])

    def test_404_invalid_question_creation(self):
        """Test if 422 returns when individual question creation is invalid"""
        new_q= {
            'question':'Who is that?'
            # no other data submitted
        }
        res = self.client().post('/questions', json=new_q)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_search(self):
        """Test question search"""
        search_data= {
            'searchTerm':'Who',
        }
        res = self.client().post('/questions/search', json=search_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])

    def test_404_invalid_search(self):
        """Test if 404 is returned with invalid search data"""
        search_data= {
            'search':'Who', #should be 'searchTerm'
        }
        res = self.client().post('/questions/search', json=search_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertTrue(data['message'])

    def test_question_by_category(self):
        """Test retrieving questions by category"""
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 4) #should be 4 q's
        

    def test_quizzes(self):
        """Test quizzes endpoint"""
        quizzes_data= {
            'previous_questions':[16, 17],
            'quiz_category':{'id':2}
        }
        res = self.client().post('/quizzes', json=quizzes_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])
        self.assertTrue(data['previous_questions'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
