import datetime
import re
from urllib import response

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
        question.choice_set.create(choice_text='respuesta1')
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["latest_question_list"],[question])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future question exist, only past questions are
        displayed
        """
        past_question = create_question(question_text="Past question", days=-30)
        future_question = create_question(question_text="Future question", days=30)
        past_question.choice_set.create(choice_text='respuesta1')
        future_question.choice_set.create(choice_text='respuesta2')
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[past_question])


    def test_two_past_questions(self):
        """
        The question index page may display multiple questions
        """
        past_question1 = create_question(question_text="Past question 1", days=-30)
        past_question2 = create_question(question_text="Past question 2", days=-40)
        past_question1.choice_set.create(choice_text='respuesta1')
        past_question2.choice_set.create(choice_text='respuesta2')
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

    def test_no_question_without_choices(self):
        """A question without choice can't be created"""
        question1 = create_question(question_text="question 1", days=30)
        question2 = create_question(question_text="question 2", days=40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[])

    def test_question_with_choices(self):
        """A question without choice can't be created"""
        question1 = create_question(question_text="question 1", days=-30)
        question2 = create_question(question_text="question 2", days=-40)
        question1.choice_set.create(choice_text='respuesta1')
        question2.choice_set.create(choice_text='respuesta2')
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[question1,question2])


class QuestionDetailViewTest(TestCase):
    
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 error not found
        """
        future_question = create_question(question_text="Future question", days=30)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past displays the 
        question's text
        """
        past_question = create_question(question_text="past question", days=-30)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

class QuestionResultsViewTest(TestCase):
    
    def test_results_one_choice(self):
        question = create_question(question_text="question", days=-30)
        choice = question.choice_set.create(choice_text='respuesta')
        url = reverse("polls:results", args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, choice.choice_text)

    def test_results_two_choices(self):
        question = create_question(question_text="question", days=-30)
        choice1 = question.choice_set.create(choice_text='respuesta1')
        choice2 = question.choice_set.create(choice_text='respuesta2')

        url = reverse("polls:results", args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, choice1.choice_text)
        self.assertContains(response, choice2.choice_text)

