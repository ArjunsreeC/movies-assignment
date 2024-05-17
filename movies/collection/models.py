from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    genres = models.TextField(default="")
    uuid = models.TextField(unique=True, editable=False)

    def __str__(self):
        return self.title

class Collection(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    movies = models.ManyToManyField(Movie, related_name='collections')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.title
