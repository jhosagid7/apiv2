"""
Test /certificate
"""
from random import choice, randint
from django.urls.base import reverse_lazy
from rest_framework import status
from ..mixins import AdmissionsTestCase


class CertificateTestSuite(AdmissionsTestCase):
    """
    🔽🔽🔽 Auth
    """
    def test_academy_schedule__without_auth(self):
        """Test /certificate without auth"""
        url = reverse_lazy('admissions:academy_schedule')
        response = self.client.get(url)
        json = response.json()

        self.assertEqual(
            json, {
                'detail': 'Authentication credentials were not provided.',
                'status_code': status.HTTP_401_UNAUTHORIZED
            })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_academy_schedule__without_capability(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        url = reverse_lazy('admissions:academy_schedule')
        self.generate_models(authenticate=True)
        response = self.client.get(url)
        json = response.json()
        expected = {
            'status_code': 403,
            'detail': "You (user: 1) don't have this capability: read_certificate for academy 1"
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.all_syllabus_schedule_dict(), [])

    """
    🔽🔽🔽 Without data
    """

    def test_academy_schedule__with_schedule_of_other_academy(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        syllabus_schedule = {'academy_id': 2}
        model = self.generate_models(authenticate=True,
                                     syllabus_schedule=syllabus_schedule,
                                     academy=2,
                                     profile_academy=True,
                                     capability='read_certificate',
                                     role='potato')
        url = reverse_lazy('admissions:academy_schedule')
        response = self.client.get(url)
        json = response.json()
        expected = []

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [])

    """
    🔽🔽🔽 With data
    """

    def test_academy_schedule(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     syllabus_schedule=True,
                                     profile_academy=True,
                                     capability='read_certificate',
                                     role='potato',
                                     syllabus=True)
        url = reverse_lazy('admissions:academy_schedule')
        response = self.client.get(url)
        json = response.json()
        expected = [{
            'id': model.syllabus_schedule.id,
            'name': model.syllabus_schedule.name,
            'description': model.syllabus_schedule.description,
            'syllabus': model.syllabus_schedule.syllabus.id,
        }]

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [{**self.model_to_dict(model, 'syllabus')}])

    """
    🔽🔽🔽 Syllabus id in querystring
    """

    def test_academy_schedule__syllabus_id_in_querystring__bad_id(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     syllabus_schedule=True,
                                     profile_academy=True,
                                     capability='read_certificate',
                                     role='potato',
                                     syllabus=True)
        url = reverse_lazy('admissions:academy_schedule') + '?syllabus_id=9999'
        response = self.client.get(url)
        json = response.json()
        expected = []

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [{**self.model_to_dict(model, 'syllabus')}])

    def test_academy_schedule__syllabus_id_in_querystring(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     syllabus_schedule=True,
                                     profile_academy=True,
                                     capability='read_certificate',
                                     role='potato',
                                     syllabus=True)
        url = reverse_lazy('admissions:academy_schedule') + '?syllabus_id=1'
        response = self.client.get(url)
        json = response.json()
        expected = [{
            'id': model.syllabus_schedule.id,
            'name': model.syllabus_schedule.name,
            'description': model.syllabus_schedule.description,
            'syllabus': model.syllabus_schedule.syllabus.id,
        }]

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [{**self.model_to_dict(model, 'syllabus')}])

    """
    🔽🔽🔽 Syllabus slug in querystring
    """

    def test_academy_schedule__syllabus_slug_in_querystring__bad_id(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     syllabus_schedule=True,
                                     profile_academy=True,
                                     capability='read_certificate',
                                     role='potato',
                                     syllabus=True)
        url = reverse_lazy('admissions:academy_schedule') + '?syllabus_slug=they-killed-kenny'
        response = self.client.get(url)
        json = response.json()
        expected = []

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [{**self.model_to_dict(model, 'syllabus')}])

    def test_academy_schedule__syllabus_slug_in_querystring(self):
        """Test /certificate without auth"""
        self.headers(academy=1)

        syllabus_kwargs = {'slug': 'they-killed-kenny'}
        model = self.generate_models(authenticate=True,
                                     syllabus_schedule=True,
                                     profile_academy=True,
                                     capability='read_certificate',
                                     role='potato',
                                     syllabus=True,
                                     syllabus_kwargs=syllabus_kwargs)
        url = reverse_lazy('admissions:academy_schedule') + '?syllabus_slug=they-killed-kenny'
        response = self.client.get(url)
        json = response.json()
        expected = [{
            'id': model.syllabus_schedule.id,
            'name': model.syllabus_schedule.name,
            'description': model.syllabus_schedule.description,
            'syllabus': model.syllabus_schedule.syllabus.id,
        }]

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [{**self.model_to_dict(model, 'syllabus')}])

    """
    🔽🔽🔽 Delete
    """

    def test_certificate_delete_in_bulk_with_one(self):
        """Test /cohort/:id/user without auth"""
        self.headers(academy=1)
        many_fields = ['id']

        base = self.generate_models(academy=True)

        for field in many_fields:
            certificate_kwargs = {
                'logo':
                choice(['http://exampledot.com', 'http://exampledotdot.com', 'http://exampledotdotdot.com']),
                'week_hours':
                randint(0, 999999999),
                'schedule_type':
                choice(['PAR-TIME', 'FULL-TIME']),
            }
            model = self.generate_models(authenticate=True,
                                         profile_academy=True,
                                         capability='crud_certificate',
                                         role='potato',
                                         certificate_kwargs=certificate_kwargs,
                                         syllabus=True,
                                         syllabus_schedule=True,
                                         models=base)
            url = (reverse_lazy('admissions:academy_schedule') + f'?{field}=' +
                   str(getattr(model['syllabus_schedule'], field)))
            response = self.client.delete(url)

            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_certificate_delete_without_auth(self):
        """Test /cohort/:id/user without auth"""
        url = reverse_lazy('admissions:academy_schedule')
        response = self.client.delete(url)
        json = response.json()
        expected = {'detail': 'Authentication credentials were not provided.', 'status_code': 401}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_certificate_delete_without_args_in_url_or_bulk(self):
        """Test /cohort/:id/user without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     capability='crud_certificate',
                                     role='potato')
        url = reverse_lazy('admissions:academy_schedule')
        response = self.client.delete(url)
        json = response.json()
        expected = {'detail': 'Missing parameters in the querystring', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_certificate_delete_in_bulk_with_two(self):
        """Test /cohort/:id/user without auth"""
        self.headers(academy=1)
        many_fields = ['id']

        base = self.generate_models(academy=True)

        for field in many_fields:
            certificate_kwargs = {
                'logo':
                choice(['http://exampledot.com', 'http://exampledotdot.com', 'http://exampledotdotdot.com']),
                'week_hours':
                randint(0, 999999999),
                'schedule_type':
                choice(['PAR-TIME', 'FULL-TIME']),
            }
            model1 = self.generate_models(authenticate=True,
                                          profile_academy=True,
                                          capability='crud_certificate',
                                          role='potato',
                                          certificate_kwargs=certificate_kwargs,
                                          syllabus=True,
                                          syllabus_schedule=True,
                                          models=base)

            model2 = self.generate_models(profile_academy=True,
                                          capability='crud_certificate',
                                          role='potato',
                                          certificate_kwargs=certificate_kwargs,
                                          syllabus=True,
                                          syllabus_schedule=True,
                                          models=base)

            url = (reverse_lazy('admissions:academy_schedule') + f'?{field}=' +
                   str(getattr(model1['syllabus_schedule'], field)) + ',' +
                   str(getattr(model2['syllabus_schedule'], field)))
            response = self.client.delete(url)

            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_academy_schedule__post__without_syllabus(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     capability='crud_certificate',
                                     role='potato')
        url = reverse_lazy('admissions:academy_schedule')
        response = self.client.post(url)
        json = response.json()
        expected = {
            'detail': 'missing-syllabus-in-request',
            'status_code': 400,
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_academy_schedule__post__syllabus_not_found(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     capability='crud_certificate',
                                     role='potato')
        url = reverse_lazy('admissions:academy_schedule')
        data = {'syllabus': 1}
        response = self.client.post(url, data)
        json = response.json()
        expected = {
            'detail': 'syllabus-not-found',
            'status_code': 404,
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_academy_schedule__post__without_academy(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     syllabus=True,
                                     capability='crud_certificate',
                                     role='potato')
        url = reverse_lazy('admissions:academy_schedule')
        data = {'syllabus': 1}
        response = self.client.post(url, data)
        json = response.json()
        expected = {'detail': 'missing-academy-in-request', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_academy_schedule__post__academy_not_found(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     syllabus=True,
                                     capability='crud_certificate',
                                     role='potato')
        url = reverse_lazy('admissions:academy_schedule')
        data = {'syllabus': 1, 'academy': 2}
        response = self.client.post(url, data)
        json = response.json()
        expected = {'detail': 'academy-not-found', 'status_code': 404}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_academy_schedule__post__without_body(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     syllabus=True,
                                     capability='crud_certificate',
                                     role='potato')
        url = reverse_lazy('admissions:academy_schedule')
        data = {'syllabus': 1, 'academy': 1}
        response = self.client.post(url, data)
        json = response.json()
        expected = {
            'name': ['This field is required.'],
            'description': ['This field is required.'],
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_academy_schedule__post(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     syllabus=True,
                                     capability='crud_certificate',
                                     role='potato')
        url = reverse_lazy('admissions:academy_schedule')
        data = {
            'academy': 1,
            'syllabus': 1,
            'name': 'They killed kenny',
            'description': 'Oh my god!',
        }
        response = self.client.post(url, data)
        json = response.json()

        self.assertDatetime(json['created_at'])
        del json['created_at']

        self.assertDatetime(json['updated_at'])
        del json['updated_at']

        expected = {
            'id': 1,
            'schedule_type': 'PART-TIME',
            'syllabus': 1,
            **data,
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.all_syllabus_schedule_dict(), [{
            'id': 1,
            'name': 'They killed kenny',
            'description': 'Oh my god!',
            'schedule_type': 'PART-TIME',
            'syllabus_id': 1,
            'academy_id': 1,
        }])
