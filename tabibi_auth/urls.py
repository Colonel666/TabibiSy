from django.urls import path

from tabibi_auth.views import register_view, get_token_view, refresh_token_view, get_current_info_view

app_name = 'tabibi_core'

urlpatterns = [
    path('register', register_view, name='register'),
    path('get_token', get_token_view, name='get_token'),
    path('refresh_token', refresh_token_view, name='refresh_token'),
    path('get_current_info', get_current_info_view, name='get_current_info'),
]
