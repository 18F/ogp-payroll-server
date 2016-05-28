from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from . import factories


class CountyTests(APITestCase):
    def setUp(self):

        county1 = factories.CountyFactory()
        county2 = factories.CountyFactory()

    def test_list_counties_succeeds(self):
        url = reverse('county-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_counties_correct_count(self):
        url = reverse('county-list')
        response = self.client.get(url, format='json')
        self.assertEqual(len(response.data), 2)

    def test_list_counties_contains_urls(self):
        url = reverse('county-list')
        response = self.client.get(url, format='json')
        self.assertIn('/county/', response.data[0]['url'])

    def test_get_single_county(self):
        # TODO: can't figure out the name to reverse
        url = '/county/1/'
        # url = reverse('county-list')
        response = self.client.get(url, format='json')
        self.assertIn('name', response.data)
        self.assertIn('us_state', response.data)


class WageDeterminationTests(APITestCase):
    def setUp(self):

        wd1 = factories.WageDeterminationFactory()
        wd2 = factories.WageDeterminationFactory()

    def test_list_wage_determination_succeeds(self):
        url = reverse('wagedetermination-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
