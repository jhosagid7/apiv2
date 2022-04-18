"""
Test /certificate
"""
from django.urls.base import reverse_lazy
from rest_framework import status
from ..mixins import AdmissionsTestCase


class CertificateTestSuite(AdmissionsTestCase):
    """Test /certificate"""
    def test_syllabus_without_auth(self):
        """Test /certificate without auth"""
        url = reverse_lazy('admissions:syllabus')
        response = self.client.get(url)
        json = response.json()

        self.assertEqual(
            json, {
                'detail': 'Authentication credentials were not provided.',
                'status_code': status.HTTP_401_UNAUTHORIZED
            })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_syllabus_without_capability(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        url = reverse_lazy('admissions:syllabus')
        self.generate_models(authenticate=True)
        response = self.client.get(url)
        json = response.json()
        expected = {
            'status_code': 403,
            'detail': "You (user: 1) don't have this capability: read_syllabus for academy 1"
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.all_syllabus_schedule_dict(), [])

    def test_syllabus_without_syllabus(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     syllabus_schedule=True,
                                     profile_academy=True,
                                     capability='read_syllabus',
                                     role='potato')
        url = reverse_lazy('admissions:syllabus')
        response = self.client.get(url)
        json = response.json()
        expected = []

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [])

    def test_syllabus(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     syllabus_schedule=True,
                                     profile_academy=True,
                                     capability='read_syllabus',
                                     role='potato',
                                     syllabus=True)
        url = reverse_lazy('admissions:syllabus')
        response = self.client.get(url)
        json = response.json()
        expected = [{
            'main_technologies': None,
            'slug': model.syllabus.slug,
            'name': model.syllabus.name,
            'academy_owner': model.syllabus.academy_owner.id,
            'duration_in_days': model.syllabus.duration_in_days,
            'duration_in_hours': model.syllabus.duration_in_hours,
            'week_hours': model.syllabus.week_hours,
            'github_url': model.syllabus.github_url,
            'id': model.syllabus.id,
            'logo': model.syllabus.logo,
            'private': model.syllabus.private,
            'created_at': self.datetime_to_iso(model.syllabus.created_at),
            'updated_at': self.datetime_to_iso(model.syllabus.updated_at),
        }]

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [{**self.model_to_dict(model, 'syllabus')}])

    def test_syllabus_post_without_capabilities(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True)
        url = reverse_lazy('admissions:syllabus')
        data = {}
        response = self.client.post(url, data)
        json = response.json()
        expected = {
            'detail': "You (user: 1) don't have this capability: crud_syllabus "
            'for academy 1',
            'status_code': 403
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.all_syllabus_dict(), [])

    def test_syllabus__post__missing_slug_in_request(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     capability='crud_syllabus',
                                     role='potato')
        url = reverse_lazy('admissions:syllabus')
        data = {}
        response = self.client.post(url, data, format='json')
        json = response.json()

        expected = {'detail': 'missing-slug', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.all_syllabus_dict(), [])

    def test_syllabus__post__missing_name_in_request(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     capability='crud_syllabus',
                                     role='potato')
        url = reverse_lazy('admissions:syllabus')
        data = {'slug': 'they-killed-kenny'}
        response = self.client.post(url, data, format='json')
        json = response.json()

        expected = {'detail': 'missing-name', 'status_code': 400}

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.all_syllabus_dict(), [])

    def test_syllabus__post(self):
        """Test /certificate without auth"""
        self.headers(academy=1)
        model = self.generate_models(authenticate=True,
                                     profile_academy=True,
                                     capability='crud_syllabus',
                                     role='potato')
        url = reverse_lazy('admissions:syllabus')
        data = {
            'slug': 'they-killed-kenny',
            'name': 'They killed kenny',
        }
        response = self.client.post(url, data, format='json')
        json = response.json()

        expected = {
            'academy_owner': 1,
            'duration_in_days': None,
            'duration_in_hours': None,
            'github_url': None,
            'id': 1,
            'logo': None,
            'private': False,
            'week_hours': None,
            **data,
        }

        self.assertEqual(json, expected)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.all_syllabus_dict(), [{
            'main_technologies': None,
            'academy_owner_id': 1,
            'duration_in_days': None,
            'duration_in_hours': None,
            'github_url': None,
            'id': 1,
            'logo': None,
            'private': False,
            'week_hours': None,
            **data,
        }])

    """
    🔽🔽🔽 Pagination
    """

    def test_syllabus__with_data__without_pagination__get_just_100(self):
        """Test /certificate without auth"""
        self.headers(academy=1)

        base = self.generate_models(authenticate=True,
                                    profile_academy=True,
                                    capability='read_syllabus',
                                    role='potato')

        models = [self.generate_models(syllabus=True, models=base) for _ in range(0, 105)]
        url = reverse_lazy('admissions:syllabus')
        response = self.client.get(url)
        json = response.json()

        self.assertEqual(json, [{
            'main_technologies': None,
            'slug': model.syllabus.slug,
            'name': model.syllabus.name,
            'academy_owner': model.syllabus.academy_owner.id,
            'duration_in_days': model.syllabus.duration_in_days,
            'duration_in_hours': model.syllabus.duration_in_hours,
            'week_hours': model.syllabus.week_hours,
            'github_url': model.syllabus.github_url,
            'id': model.syllabus.id,
            'logo': model.syllabus.logo,
            'private': model.syllabus.private,
            'created_at': self.datetime_to_iso(model.syllabus.created_at),
            'updated_at': self.datetime_to_iso(model.syllabus.updated_at),
        } for model in models if model['syllabus'].id <= 100])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [{
            **self.model_to_dict(model, 'syllabus'),
        } for model in models])

    def test_syllabus__with_data__with_pagination__first_five(self):
        """Test /certificate without auth"""
        self.headers(academy=1)

        base = self.generate_models(authenticate=True,
                                    profile_academy=True,
                                    capability='read_syllabus',
                                    role='potato')

        models = [self.generate_models(syllabus=True, models=base) for _ in range(0, 10)]
        url = reverse_lazy('admissions:syllabus') + '?limit=5&offset=0'
        response = self.client.get(url)
        json = response.json()

        self.assertEqual(
            json, {
                'count':
                10,
                'first':
                None,
                'last':
                'http://testserver/v1/admissions/syllabus?limit=5&offset=5',
                'next':
                'http://testserver/v1/admissions/syllabus?limit=5&offset=5',
                'previous':
                None,
                'results': [{
                    'main_technologies': None,
                    'slug': model.syllabus.slug,
                    'name': model.syllabus.name,
                    'academy_owner': model.syllabus.academy_owner.id,
                    'duration_in_days': model.syllabus.duration_in_days,
                    'duration_in_hours': model.syllabus.duration_in_hours,
                    'week_hours': model.syllabus.week_hours,
                    'github_url': model.syllabus.github_url,
                    'id': model.syllabus.id,
                    'logo': model.syllabus.logo,
                    'private': model.syllabus.private,
                    'created_at': self.datetime_to_iso(model.syllabus.created_at),
                    'updated_at': self.datetime_to_iso(model.syllabus.updated_at),
                } for model in models if model['syllabus'].id <= 5]
            })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [{
            **self.model_to_dict(model, 'syllabus'),
        } for model in models])

    def test_syllabus__with_data__with_pagination__last_five(self):
        """Test /certificate without auth"""
        self.headers(academy=1)

        base = self.generate_models(authenticate=True,
                                    profile_academy=True,
                                    capability='read_syllabus',
                                    role='potato')

        models = [self.generate_models(syllabus=True, models=base) for _ in range(0, 10)]
        url = reverse_lazy('admissions:syllabus') + '?limit=5&offset=5'
        response = self.client.get(url)
        json = response.json()

        self.assertEqual(
            json, {
                'count':
                10,
                'first':
                'http://testserver/v1/admissions/syllabus?limit=5',
                'last':
                None,
                'next':
                None,
                'previous':
                'http://testserver/v1/admissions/syllabus?limit=5',
                'results': [{
                    'main_technologies': None,
                    'slug': model.syllabus.slug,
                    'name': model.syllabus.name,
                    'academy_owner': model.syllabus.academy_owner.id,
                    'duration_in_days': model.syllabus.duration_in_days,
                    'duration_in_hours': model.syllabus.duration_in_hours,
                    'week_hours': model.syllabus.week_hours,
                    'github_url': model.syllabus.github_url,
                    'id': model.syllabus.id,
                    'logo': model.syllabus.logo,
                    'private': model.syllabus.private,
                    'created_at': self.datetime_to_iso(model.syllabus.created_at),
                    'updated_at': self.datetime_to_iso(model.syllabus.updated_at),
                } for model in models if model['syllabus'].id > 5],
            })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [{
            **self.model_to_dict(model, 'syllabus'),
        } for model in models])

    def test_syllabus__with_data__with_pagination__after_last_five(self):
        """Test /certificate without auth"""
        self.headers(academy=1)

        base = self.generate_models(authenticate=True,
                                    profile_academy=True,
                                    capability='read_syllabus',
                                    role='potato')

        models = [self.generate_models(syllabus=True, models=base) for _ in range(0, 10)]
        url = reverse_lazy('admissions:syllabus') + '?limit=5&offset=10'
        response = self.client.get(url)
        json = response.json()

        self.assertEqual(
            json, {
                'count': 10,
                'first': 'http://testserver/v1/admissions/syllabus?limit=5',
                'last': None,
                'next': None,
                'previous': 'http://testserver/v1/admissions/syllabus?limit=5&offset=5',
                'results': [],
            })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.all_syllabus_dict(), [{
            **self.model_to_dict(model, 'syllabus'),
        } for model in models])
