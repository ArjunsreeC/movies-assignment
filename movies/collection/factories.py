import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from .models import Movie, Collection

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')

class MovieFactory(DjangoModelFactory):
    class Meta:
        model = Movie

    title = factory.Faker('sentence')
    description = factory.Faker('text')
    genres = factory.Faker('word')
    uuid = factory.Faker('uuid4')

class CollectionFactory(DjangoModelFactory):
    class Meta:
        model = Collection

    title = factory.Faker('sentence')
    description = factory.Faker('text')
    creator = factory.SubFactory(UserFactory)
