# tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Collection, Movie
from .factories import CollectionFactory, MovieFactory, UserFactory

class CollectionTests(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_create_collection_with_movies(self):
        movie_data = {
            'uuid': str(factory.Faker('uuid4').generate()),
            'title': 'Test Movie',
            'description': 'Test Description',
            'genres': 'Drama'
        }
        collection_data = {
            'title': 'Test Collection',
            'description': 'Test Description',
            'movies': [movie_data]
        }

        url = reverse('collection-list')  # Adjust to your URL name
        response = self.client.post(url, collection_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('collection_uuid', response.data)
        collection = Collection.objects.get(id=response.data['collection_uuid'])
        self.assertEqual(collection.movies.count(), 1)
        self.assertEqual(collection.movies.first().title, 'Test Movie')

    def test_update_collection_with_movies(self):
        collection = CollectionFactory(creator=self.user)
        movie1 = MovieFactory()
        collection.movies.add(movie1)

        new_movie_data = {
            'uuid': str(factory.Faker('uuid4').generate()),
            'title': 'Updated Movie',
            'description': 'Updated Description',
            'genres': 'Action'
        }
        updated_collection_data = {
            'title': 'Updated Collection',
            'description': 'Updated Description',
            'movies': [new_movie_data]
        }

        url = reverse('collection-detail', kwargs={'pk': collection.id})  # Adjust to your URL name
        response = self.client.put(url, updated_collection_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('collection_uuid', response.data)
        updated_collection = Collection.objects.get(id=response.data['collection_uuid'])
        self.assertEqual(updated_collection.movies.count(), 1)
        self.assertEqual(updated_collection.movies.first().title, 'Updated Movie')

    def test_partial_update_collection(self):
        collection = CollectionFactory(creator=self.user)
        movie1 = MovieFactory()
        collection.movies.add(movie1)

        partial_update_data = {
            'title': 'Partially Updated Collection'
        }

        url = reverse('collection-detail', kwargs={'pk': collection.id})  # Adjust to your URL name
        response = self.client.patch(url, partial_update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_collection = Collection.objects.get(id=collection.id)
        self.assertEqual(updated_collection.title, 'Partially Updated Collection')
        self.assertEqual(updated_collection.movies.count(), 1)
        self.assertEqual(updated_collection.movies.first().title, movie1.title)
