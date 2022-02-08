import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse


from .models import Question

class QuestionModelTest(TestCase):
    
    def test_was_published_recently_with_future_questions(self):
        """was_published_recently returns False for questions whose pub_date is in the future"""

        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text="¿Quien es el mejor Course Director de platzi", pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_past_questions(self):
        """was_published_recently returns False for questions whose pub_date is in the past"""

        time = timezone.now() - datetime.timedelta(days=30)
        future_question = Question(question_text="¿Quien es el mejor Course Director de platzi", pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_present_questions(self):
        """was_published_recently returns False for questions whose pub_date is in the present"""

        time = timezone.now()
        future_question = Question(question_text="¿Quien es el mejor Course Director de platzi", pub_date=time)
        self.assertIs(future_question.was_published_recently(), True)

def create_question(question_text,days):
    """
    Create a question with the given "question_text",  and published 
    the given number of days offset to now(negative for questions published in the past
    , positive por question that have yet to be published)
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text,pub_date=time)

class QuestionIndexViewTest(TestCase):

    def test_no_question(self):
        """If no question exist, an appropiate message is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"],[])

    def test_no_future_question_displayed(self):
        """Questions with a pub_date in the future aren't displayed on the index page"""

        create_question(question_text="Future Question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["latest_question_list"],[])

    def test_past_question(self):
        """Questions with a pub_date in the past are displayed on the index page"""
        
        question = create_question(question_text="Future Question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["latest_question_list"],[question])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future question exist, only past questions are
        displayed
        """
        past_question = create_question(question_text="Past question", days=-30)
        furute_question = create_question(question_text="Future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[past_question])


    def test_two_past_questions(self):
        """
        The question index page may display multiple questions
        """
        past_question1 = create_question(question_text="Past question 1", days=-30)
        past_question2 = create_question(question_text="Past question 2", days=-40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[past_question1, past_question2])

    def test_two_future_questions(self):
        """
        The question index page may display multiple questions
        """
        Future_question1 = create_question(question_text="Future question 1", days=30)
        future_question2 = create_question(question_text="Future question 2", days=40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[])

        
