from django.urls import path

from  .views import create_user_view, login_view, ContactModify

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', create_user_view, name='register'),
    path('contactmodify/', ContactModify.as_view(), name='contactmodify'),
]