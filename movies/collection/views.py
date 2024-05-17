import requests
from time import sleep
from rest_framework import viewsets, status
from rest_framework.response import Response
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from .models import Collection, Movie
from .serializers import CollectionSerializer, MovieSerializer

@csrf_exempt
def get_movies(request):

    api_url = settings.EXTERNAL_API_URL
    page = request.GET.get('page', 1)
    page_size = 10
    retries = 3

    for attempt in range(retries):
        try:
            response = response = requests.get(
                api_url,
                params={'page': page, 'page_size': page_size},
                auth=HTTPBasicAuth(settings.EXTERNAL_API_USERNAME, settings.EXTERNAL_API_PASSWORD),
                verify=False
            )
            response.raise_for_status()
            break
        except (requests.exceptions.RequestException, IOError) as e:
            if attempt < retries - 1:
                sleep(1)
                continue
            else:
                return JsonResponse({'error': str(e)}, status=500)
            
    if response.status_code == 200:
        movies_data = response.json()
        print(movies_data)
        count = movies_data.get('count', 0)
        next_page = movies_data.get('next', None)
        previous_page = movies_data.get('previous', None)
        movies = movies_data.get('results', [])

        formatted_movies = []
        for movie in movies:
            formatted_movie = {
                'title': movie.get('title', ''),
                'description': movie.get('description', ''),
                'genres': movie.get('genres', ''),
                'uuid': movie.get('uuid', '')
            }
            formatted_movies.append(formatted_movie)

        return JsonResponse({
            'count': count,
            'next': next_page,
            'previous': previous_page,
            'data': formatted_movies
        })
    else:
        return JsonResponse({'error': 'Failed to fetch movies'}, status=response.status_code)

class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    def list(self, request, *args, **kwargs):

        user = request.user.id if request.user.id else 1
        queryset = Collection.objects.filter(creator=user)
        serializer = self.get_serializer(queryset, many=True)
        collection_data = serializer.data

        formatted_collections = [
            {
                "title": collection["title"],
                "uuid": collection["id"],
                "description": collection["description"]
            } for collection in collection_data
        ]

        favourite_genres = self.get_favourite_genres(queryset)

        response_data = {
            "is_success": True,
            "data": {
                "collections": formatted_collections,
                "favourite_genres": favourite_genres
            }
        }

        return Response(response_data)
    
    def get_favourite_genres(self, collections):
        genre_counter = {}
        for collection in collections:
            for movie in collection.movies.all():
                genres = movie.genres.split(',')
                for genre in genres:
                    genre = genre.strip()
                    genre_counter[genre] = genre_counter.get(genre, 0) + 1

        sorted_genres = sorted(genre_counter.items(), key=lambda item: item[1], reverse=True)
        top_3_genres = [genre for genre, count in sorted_genres[:3]]

        return ", ".join(top_3_genres)
    
    def create(self, request, *args, **kwargs):
        collection_data = request.data
        movies_data = collection_data.pop('movies', [])
        collection_serializer = self.get_serializer(data=collection_data)

        if collection_serializer.is_valid():
            try:
                with transaction.atomic():
                    collection_instance = collection_serializer.save()
                    for movie_data in movies_data:
                        uuid = movie_data.get('uuid')
                        movie_instance, created = Movie.objects.get_or_create(
                            uuid=uuid,
                            defaults=movie_data
                        )
                        if not created:
                            for key, value in movie_data.items():
                                setattr(movie_instance, key, value)
                            movie_instance.save()
                        collection_instance.movies.add(movie_instance)
                    collection_instance.save()
                    response_data = {
                        'collection_uuid': str(collection_instance.id)  # Assuming the ID is a UUID field
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(collection_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        collection_data = request.data
        movies_data = collection_data.pop('movies', [])

        collection_serializer = self.get_serializer(instance, data=collection_data, partial=partial)

        if collection_serializer.is_valid():
            try:
                with transaction.atomic():
                    
                    collection_instance = collection_serializer.save()
                    collection_instance.movies.clear()

                    for movie_data in movies_data:
                        uuid = movie_data.get('uuid')
                        if uuid:
                            movie_instance, created = Movie.objects.get_or_create(
                                uuid=uuid,
                                defaults=movie_data
                            )
                            if not created:
                                for key, value in movie_data.items():
                                    setattr(movie_instance, key, value)
                                movie_instance.save()
                            collection_instance.movies.add(movie_instance)
                    
                    collection_instance.save()
                    response_data = {
                        'collection_uuid': str(collection_instance.id)
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(collection_serializer.errors, status=status.HTTP_400_BAD_REQUEST)