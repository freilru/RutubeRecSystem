from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.user_login, name='login'),
    path('logout', LogoutView.as_view(next_page='index'), name='logout'),
    path('send_reaction/', views.send_reaction, name='send_reaction'),
    path('send_search/', views.send_search, name='send_search'),
    path('profile/', views.profile, name='profile'),
    path('shorts/', views.shorts, name='shorts'),
    path('send_shorts_reaction/', views.send_shorts_reaction, name='send_shorts_reaction'),
]
