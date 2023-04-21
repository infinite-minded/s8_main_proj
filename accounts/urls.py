from django.urls import path

from  .views import create_user_view, login_view, ContactModify, ContactDelete, EmergencySMS

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', create_user_view, name='register'),
    path('contactmodify/', ContactModify.as_view(), name='contactmodify'),
    path('contactdelete/', ContactDelete.as_view(), name='contactdelete'),
    path('alert/', EmergencySMS.as_view(), name='alert'),
]