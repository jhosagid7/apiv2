"""
Test /answer/:id
"""
import re
from datetime import datetime
from unittest.mock import patch, MagicMock, call
from django.urls.base import reverse_lazy
from rest_framework import status
from breathecode.services.datetime_to_iso_format import datetime_to_iso_format
from breathecode.tests.mocks import (
    GOOGLE_CLOUD_PATH,
    apply_google_cloud_client_mock,
    apply_google_cloud_bucket_mock,
    apply_google_cloud_blob_mock,
)
from ..mixins import FeedbackTestCase
from ...signals import survey_answered


class AnswerIdTestSuite(FeedbackTestCase):
    """Test /answer/:id"""
    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    def test_answer_id_without_auth(self):
        """Test /answer/:id without auth"""
        url = reverse_lazy('feedback:user_me_answer_id', kwargs={'answer_id': 9999})
        response = self.client.get(url)
        json = response.json()
        expected = {'detail': 'Authentication credentials were not provided.', 'status_code': 401}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.count_answer(), 0)

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    def test_answer_id_without_data(self):
        """Test /answer/:id without auth"""
        self.generate_models(authenticate=True)
        url = reverse_lazy('feedback:user_me_answer_id', kwargs={'answer_id': 9999})
        response = self.client.get(url)
        json = response.json()
        expected = {
            'detail': 'answer-of-other-user-or-not-exists',
            'status_code': 404,
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.count_answer(), 0)

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    def test_answer_id__answer_of_other_user(self):
        """Test /answer/:id without auth"""
        self.generate_models(authenticate=True)
        model = self.generate_models(answer=True)
        db = self.model_to_dict(model, 'answer')
        url = reverse_lazy('feedback:user_me_answer_id', kwargs={'answer_id': model['answer'].id})
        response = self.client.get(url)
        json = response.json()
        expected = {'detail': 'answer-of-other-user-or-not-exists', 'status_code': 404}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.all_answer_dict(), [db])

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    def test_answer_id_with_data(self):
        """Test /answer/:id without auth"""
        answer_kwargs = {'status': 'SENT'}
        model = self.generate_models(authenticate=True, answer=True, user=True, answer_kwargs=answer_kwargs)

        db = self.model_to_dict(model, 'answer')
        url = reverse_lazy('feedback:user_me_answer_id', kwargs={'answer_id': model['answer'].id})
        response = self.client.get(url)
        json = response.json()
        expected = {
            'id': model['answer'].id,
            'title': model['answer'].title,
            'lowest': model['answer'].lowest,
            'highest': model['answer'].highest,
            'lang': model['answer'].lang,
            'score': model['answer'].score,
            'comment': model['answer'].comment,
            'status': model['answer'].status,
            'opened_at': model['answer'].opened_at,
            'created_at': datetime_to_iso_format(model['answer'].created_at),
            'updated_at': datetime_to_iso_format(model['answer'].updated_at),
            'cohort': model['answer'].cohort,
            'academy': model['answer'].academy,
            'mentor': {
                'first_name': model['answer'].mentor.first_name,
                'id': model['answer'].mentor.id,
                'last_name': model['answer'].mentor.last_name,
                'profile': None,
            },
            'user': {
                'first_name': model['answer'].user.first_name,
                'id': model['answer'].user.id,
                'last_name': model['answer'].user.last_name,
                'profile': None,
            },
            'event': model['answer'].event,
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_answer_dict(), [db])

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    @patch('breathecode.feedback.signals.survey_answered.send', MagicMock())
    def test_answer_id_put_with_bad_id(self):
        """Test /answer/:id without auth"""
        self.generate_models(authenticate=True)
        url = reverse_lazy('feedback:user_me_answer_id', kwargs={'answer_id': 9999})
        response = self.client.put(url, {})
        json = response.json()
        expected = {
            'detail': 'answer-of-other-user-or-not-exists',
            'status_code': 404,
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(survey_answered.send.call_args_list, [])

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    @patch('breathecode.feedback.signals.survey_answered.send', MagicMock())
    def test_answer_id_put_without_score(self):
        """Test /answer/:id without auth"""
        answer_kwargs = {'status': 'SENT'}
        model = self.generate_models(authenticate=True, answer=True, user=True, answer_kwargs=answer_kwargs)
        db = self.model_to_dict(model, 'answer')
        data = {
            'comment': 'They killed kenny',
        }
        url = reverse_lazy('feedback:user_me_answer_id', kwargs={'answer_id': model['answer'].id})
        response = self.client.put(url, data)
        json = response.json()

        self.assertEqual(json, {'non_field_errors': ['Score must be between 1 and 10']})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.all_answer_dict(), [db])
        self.assertEqual(survey_answered.send.call_args_list, [])

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    @patch('breathecode.feedback.signals.survey_answered.send', MagicMock())
    def test_answer_id_put_with_score_less_of_1(self):
        """Test /answer/:id without auth"""
        answer_kwargs = {'status': 'SENT'}
        model = self.generate_models(authenticate=True, answer=True, user=True, answer_kwargs=answer_kwargs)
        db = self.model_to_dict(model, 'answer')
        url = reverse_lazy('feedback:user_me_answer_id', kwargs={'answer_id': model['answer'].id})
        data = {
            'comment': 'They killed kenny',
            'score': 0,
        }
        response = self.client.put(url, data)
        json = response.json()

        self.assertEqual(json, {'non_field_errors': ['Score must be between 1 and 10']})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.all_answer_dict(), [db])
        self.assertEqual(survey_answered.send.call_args_list, [])

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    @patch('breathecode.feedback.signals.survey_answered.send', MagicMock())
    def test_answer_id_put_with_score_more_of_10(self):
        """Test /answer/:id without auth"""
        answer_kwargs = {'status': 'SENT'}
        model = self.generate_models(authenticate=True, answer=True, user=True, answer_kwargs=answer_kwargs)
        db = self.model_to_dict(model, 'answer')
        url = reverse_lazy('feedback:user_me_answer_id', kwargs={'answer_id': model['answer'].id})
        data = {
            'comment': 'They killed kenny',
            'score': 11,
        }
        response = self.client.put(url, data)
        json = response.json()

        self.assertEqual(json, {'non_field_errors': ['Score must be between 1 and 10']})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.all_answer_dict(), [db])
        self.assertEqual(survey_answered.send.call_args_list, [])

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    @patch('breathecode.feedback.signals.survey_answered.send', MagicMock())
    def test_answer_id_put_with_all_valid_scores(self):
        """Test /answer/:id without auth"""
        answer_kwargs = {'status': 'SENT'}
        answers = []

        for score in range(1, 10):
            self.remove_all_answer()
            model = self.generate_models(
                authenticate=True,
                answer=True,
                user=True,
                answer_kwargs=answer_kwargs,
            )
            answers.append(model.answer)
            db = self.model_to_dict(model, 'answer')
            url = reverse_lazy('feedback:user_me_answer_id', kwargs={'answer_id': model['answer'].id})

            data = {
                'comment': 'They killed kenny',
                'score': score,
            }
            response = self.client.put(url, data)
            json = response.json()

            expected = {
                'id': model['answer'].id,
                'title': model['answer'].title,
                'lowest': model['answer'].lowest,
                'highest': model['answer'].highest,
                'lang': model['answer'].lang,
                'score': score,
                'comment': data['comment'],
                'status': 'ANSWERED',
                'opened_at': model['answer'].opened_at,
                'created_at': datetime_to_iso_format(model['answer'].created_at),
                'cohort': model['answer'].cohort,
                'academy': model['answer'].academy,
                'survey': None,
                'mentorship_session': None,
                'sent_at': None,
                'mentor': model['answer'].mentor.id,
                'event': model['answer'].event,
                'user': model['answer'].user.id,
            }

            del json['updated_at']

            self.assertEqual(json, expected)

            dicts = [
                answer for answer in self.all_answer_dict() if not 'updated_at' in answer
                or isinstance(answer['updated_at'], datetime) and answer.pop('updated_at')
            ]

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            db['score'] = score
            db['status'] = 'ANSWERED'
            db['comment'] = data['comment']

            self.assertEqual(dicts, [db])

        self.assertEqual(survey_answered.send.call_args_list,
                         [call(instance=answer, sender=answer.__class__) for answer in answers])

    # # TODO: this test should return 400 but its returning 200, why? If needs to return 400 because you cannot change your score in the answer once you already answered

    # @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    # @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    # @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    # def test_answer_id_put_twice_different_score(self):
    #     """Test /answer/:id without auth"""
    #     model = self.generate_models(authenticate=True,
    #                                  answer=True,
    #                                  user=True,
    #                                  answer_score=7,
    #                                  answer_status='SENT')
    #     db = self.model_to_dict(model, 'answer')
    #     url = reverse_lazy('feedback:user_me_answer_id',
    #                        kwargs={'answer_id': model['answer'].id})
    #     data = {
    #         'comment': 'They killed kenny',
    #         'score': 1,
    #     }
    #     self.client.put(url, data)

    #     response = self.client.put(url, data)
    #     json = response.json()

    #     # assert False
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch(GOOGLE_CLOUD_PATH['client'], apply_google_cloud_client_mock())
    @patch(GOOGLE_CLOUD_PATH['bucket'], apply_google_cloud_bucket_mock())
    @patch(GOOGLE_CLOUD_PATH['blob'], apply_google_cloud_blob_mock())
    @patch('breathecode.feedback.signals.survey_answered.send', MagicMock())
    def test_answer_id_put_twice_same_score(self):
        """Test /answer/:id without auth"""
        answer_kwargs = {'status': 'SENT', 'score': 3}
        model = self.generate_models(authenticate=True, answer=True, user=True, answer_kwargs=answer_kwargs)
        db = self.model_to_dict(model, 'answer')
        url = reverse_lazy('feedback:user_me_answer_id', kwargs={'answer_id': model['answer'].id})
        data = {
            'comment': 'They killed kenny',
            'score': 3,
        }
        self.client.put(url, data)
        response = self.client.put(url, data)
        json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        db['score'] = data['score']
        db['status'] = 'ANSWERED'
        db['comment'] = data['comment']

        self.assertEqual(self.all_answer_dict(), [db])
        self.assertEqual(survey_answered.send.call_args_list,
                         [call(instance=model.answer, sender=model.answer.__class__)])
