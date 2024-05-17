from rest_framework import serializers
from .models import Collection, Movie


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class CollectionSerializer(serializers.ModelSerializer):
    movies = MovieSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'title', 'description', 'movies']
