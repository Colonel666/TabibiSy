from django.urls import path

from core.views import register

app_name = 'core'

urlpatterns = [
    # path('', index, name='index'),
    path('register', register, name='register'),
]
