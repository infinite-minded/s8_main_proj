from django.urls import path

from  .views import create_user_view, login_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', create_user_view, name='register'),
]