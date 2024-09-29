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


# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Получаем данные о реакциях пользователя
    liked_videos = Reaction.objects.filter(user=request.user, reaction_type='like').values_list('video_id', flat=True)
    disliked_videos = Reaction.objects.filter(user=request.user, reaction_type='dislike').values_list('video_id', flat=True)
    seen_videos = ShownVideo.objects.filter(user=request.user).values_list('video_id', flat=True)

    # Формируем payload для запроса
    payload = {
        "user_id": str(request.user.id),
        "items_liked": list(liked_videos),
        "items_disliked": list(disliked_videos),
        "videos_seen": list(seen_videos)
    }

    # Отправляем запрос на AI сервер
    ai_url = API_SERVER_URL + 'recommend_video'
    headers = {'Content-Type': 'application/json'}
    encoded_payload = json.dumps(payload).encode('utf-8')

    req = urllib.request.Request(ai_url, data=encoded_payload, headers=headers)
    with urllib.request.urlopen(req) as response:
        response_data = json.loads(response.read().decode('utf-8'))

    # Здесь можно обработать полученные рекомендации из response_data

    print(response_data)

    context = {
        'recommended_videos': response_data.get('recommended_videos', [])
    }

    # Обновляем информацию о показанных видео
    for video in context['recommended_videos']:
        ShownVideo.objects.update_or_create(
            user=request.user,
            video_id=video['id'],
            defaults={'shown_at': timezone.now()}
        )

    # Вывод информации о запросе в консоль
    print("Информация о запросе:")
    print(f"IP адрес клиента: {request.META.get('REMOTE_ADDR')}")
    print(f"User-Agent: {request.META.get('HTTP_USER_AGENT')}")
    print(f"Язык: {request.META.get('HTTP_ACCEPT_LANGUAGE')}")

    return render(request, 'main/main-page.html', context)


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


@login_required
def send_reaction(request):
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        reaction_type = request.POST.get('reaction_type')

        # Создаем новую реакцию или обновляем существующую
        Reaction.objects.update_or_create(
            user=request.user,
            video_id=video_id,
            defaults={'reaction_type': reaction_type}
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def send_search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        try:
            SearchQuery.objects.create(user=request.user, query=query)

            try:
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


def custom_404(request, exception):
    return redirect('index')


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


def shorts(request):
    shorts = [
        {'category': ["коты", "животные"], 'video_url': 'http://127.0.0.1:8000/static/main/videos/IMG_4745.MOV'},
        {'category': ["коты", "животные"], 'video_url': 'http://127.0.0.1:8000/static/main/videos/IMG_4745.MOV'},
        {'category': ["коты", "животные"], 'video_url': 'http://127.0.0.1:8000/static/main/videos/IMG_4745.MOV'},
    ]

    context = {
        'shorts': shorts,
    }

    return render(request, 'main/index.html', context)


@login_required
def send_shorts_reaction(request):
    '''отправить на микросервис чтоб обновить рейтинг категорий'''
    if request.method == 'POST':
        video_categories = request.POST.get('video_id')
        reaction_type = request.POST.get('reaction_type')

        user_interests = CustomUser.objects.get(id=request.user.id).interests

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
