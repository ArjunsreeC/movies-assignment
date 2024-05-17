import jwt
from django.http import JsonResponse
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

@csrf_exempt
def register_user(request):

    print(request.POST)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already taken'}, status=400)
        user = User.objects.create_user(username=username, password=password)
        auth_user = authenticate(username=username, password=password)
        if auth_user:
            access_token = generate_jwt_token(user)
            return JsonResponse({'access_token': access_token})
        else:
            return JsonResponse({'error': 'Failed to authenticate user'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
def generate_jwt_token(user):
    """
    Function to generate a JWT token for a given user.
    """
    payload = {
        'user_id': user.id,
        'exp': datetime.now() + timedelta(days=1),
        'iat': datetime.now()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token