from django.urls import path

from tabibi_auth.views import register

app_name = 'tabibi_core'

urlpatterns = [
    # path('', index, name='index'),
    path('register', register, name='register'),
]
