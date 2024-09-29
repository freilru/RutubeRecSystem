# Импорт необходимых модулей
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from RutubeRecSystem.settings import API_SERVER_URL
from main.models import CustomUser, Reaction, SearchQuery, ShownVideo
from main.forms import CustomUserCreationForm, CustomAuthenticationForm
from django.utils import timezone
from django.conf import settings
import urllib.request
import urllib.parse

# Представление для главной страницы
def index(request):
    # Проверка аутентификации пользователя
    if not request.user.is_authenticated:
        return redirect('register')
    
    # Получение данных о реакциях пользователя
    liked_videos = Reaction.objects.filter(user=request.user, reaction_type='like').values_list('video_id', flat=True)
    if not liked_videos:
        liked_videos = ['478fy4h3fu3']
    disliked_videos = Reaction.objects.filter(user=request.user, reaction_type='dislike').values_list('video_id', flat=True)
    if not disliked_videos:
        disliked_videos = ['478fy4h3fu3']
    seen_videos = ShownVideo.objects.filter(user=request.user).values_list('video_id', flat=True)
    if not seen_videos:
        seen_videos = ['478fy4h3fu3']

    # Формирование payload для запроса к AI серверу
    payload = {
        "user_id": str(request.user.id),
        "items_liked": list(liked_videos),
        "items_disliked": list(disliked_videos),
        "videos_seen": list(seen_videos)
    }

    # Отправка запроса на AI сервер
    ai_url = API_SERVER_URL + 'recommend_video'
    headers = {'Content-Type': 'application/json'}
    encoded_payload = json.dumps(payload).encode('utf-8')

    req = urllib.request.Request(ai_url, data=encoded_payload, headers=headers)
    with urllib.request.urlopen(req) as response:
        response_data = json.loads(response.read().decode('utf-8'))
        print(response_data)
        # Проверка формата ответа
        if isinstance(response_data, str):
            response_data = json.loads(response_data)

        # Обработка полученных рекомендаций
        recommended_videos = response_data if isinstance(response_data, list) else []

        print(recommended_videos)

        # Добавляем трендовые и новые видео
        import csv
        import random
        import os

        def get_random_videos(csv_file, count=5):
            with open(os.path.join(settings.BASE_DIR, 'main', 'static', 'main', 'csv', csv_file), 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                videos = list(reader)
                return random.sample(videos, min(count, len(videos)))

        trending_videos = get_random_videos('trending_videos.csv', 5)
        new_videos = get_random_videos('new_videos.csv', 5)

        # Преобразуем данные в нужный формат
        trending_videos = [{'video_id': video['video_id'], 'title': video['title'], 'description': video['description'], 'v_pub_datetime': video['v_pub_datetime'], 'category_id': video['category_id']} for video in trending_videos]
        new_videos = [{'video_id': video['video_id'], 'title': video['title'], 'description': video['description'], 'v_pub_datetime': video['v_pub_datetime'], 'category_id': video['category_id']} for video in new_videos]
        
        context = {
            'recommended_videos': recommended_videos,
            'trending_videos': trending_videos,
            'new_videos': new_videos
        }
    print(context)

    # Обновление информации о показанных видео
    for video in context['recommended_videos']:
        ShownVideo.objects.update_or_create(
            user=request.user,
            video_id=video['video_id'],
            defaults={'shown_at': timezone.now()}
        )

    # Вывод информации о запросе в консоль
    print("Информация о запросе:")
    print(f"IP адрес клиента: {request.META.get('REMOTE_ADDR')}")
    print(f"User-Agent: {request.META.get('HTTP_USER_AGENT')}")
    print(f"Язык: {request.META.get('HTTP_ACCEPT_LANGUAGE')}")

    return render(request, 'main/main-page.html', context)

# Представление для регистрации пользователя
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})

# Представление для входа пользователя
def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

# Представление для отправки реакции на видео
@login_required
def send_reaction(request):
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        reaction_type = request.POST.get('reaction_type')

        # Создание новой реакции или обновление существующей
        Reaction.objects.update_or_create(
            user=request.user,
            video_id=video_id,
            defaults={'reaction_type': reaction_type}
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

# Представление для отправки поискового запроса
@login_required
def send_search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        try:
            SearchQuery.objects.create(user=request.user, query=query)

            try:
                # Отправка запроса на AI сервер для обработки поискового запроса
                ai_url = API_SERVER_URL + 'search_query'
                headers = {'Content-Type': 'application/json'}
                payload = {
                    "query": query,
                }
                payload = json.dumps(payload).encode('utf-8')

                req = urllib.request.Request(ai_url, data=payload, headers=headers)
                with urllib.request.urlopen(req) as response:
                    response_data = json.loads(response.read().decode('utf-8'))
                
                print(response_data)
            except:
                pass

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Ошибка при сохранении поискового запроса: {e}")
            return JsonResponse({'status': 'error', 'message': 'Не удалось сохранить поисковый запрос'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'}, status=400)

# Обработчик ошибки 404
def custom_404(request, exception):
    return redirect('index')

# Представление для профиля пользователя
@login_required
def profile(request):
    user = request.user
    reactions = Reaction.objects.filter(user=user).order_by('-created_at')
    search_queries = SearchQuery.objects.filter(user=user).order_by('-created_at')
    shown_videos = ShownVideo.objects.filter(user=user).order_by('-shown_at')

    context = {
        'user': user,
        'reactions': reactions,
        'search_queries': search_queries,
        'shown_videos': shown_videos,
    }
    return render(request, 'main/profile.html', context)

# Представление для страницы с короткими видео
def shorts(request):
    shorts = [
        {'category': ["коты", "животные"], 'video_url': 'http://127.0.0.1:8000/static/main/videos/IMG_4745.MOV'},
        {'category': ["коты", "животные"], 'video_url': 'http://127.0.0.1:8000/static/main/videos/IMG_4745.MOV'},
        {'category': ["коты", "животные"], 'video_url': 'http://127.0.0.1:8000/static/main/videos/IMG_4745.MOV'},
    ]

    context = {
        'shorts': shorts,
    }

    return render(request, 'main/shorts.html', context)

# Представление для отправки реакции на короткие видео
@login_required
def send_shorts_reaction(request):
    if request.method == 'POST':
        video_categories = request.POST.get('video_id')
        reaction_type = request.POST.get('reaction_type')

        user_interests = CustomUser.objects.get(id=request.user.id).interests

        # Отправка запроса на AI сервер для обновления рейтинга категорий
        ai_url = API_SERVER_URL + 'process'
        headers = {'Content-Type': 'application/json'}
        payload = {
            "categories": user_interests,
            "reaction": 1 if reaction_type == 'like' else 0,
            "tiktok_categories": video_categories,
        }
        payload = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(ai_url, data=payload, headers=headers)
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))

        print(response_data)

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
