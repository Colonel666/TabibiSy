import datetime

from django.http import JsonResponse
from django.utils import timezone

from core.models import User, Token


def register(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    email = request.POST.get('email', '').lower()
    password1 = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email is required'}, status=400)
    if not password1 or not password2:
        return JsonResponse({'status': 'error', 'message': 'Password is required'}, status=400)
    if password1 != password2:
        return JsonResponse({'status': 'error', 'message': 'Passwords do not match'}, status=400)

    try: existing_user = User.objects.get(email__iexact=email)
    except User.DoesNotExist: existing_user = None

    if existing_user:
        if existing_user.is_active or existing_user.email_verified:
            return JsonResponse({'status': 'error', 'message': 'Email already registered'}, status=400)
        now = timezone.now()
        if abs(existing_user.created_at - now).hours > 24:
            existing_user.delete()
            existing_user = None
    if existing_user:
        return JsonResponse({'status': 'error', 'message': 'Email already registered'}, status=400)
    new_user = User.objects.create(email=email, is_active=False)
    new_user.set_password(password1)
    new_user.save()
    return JsonResponse({'status': 'ok'})


def get_token(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    email = request.POST.get('email', '').lower()
    password = request.POST.get('password', '')
    if not email or not password:
        return JsonResponse({'status': 'error', 'message': 'Email and password are required'}, status=400)

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=400)

    if not user.check_password(password):
        return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=400)

    # if not user.email_verified:
    #     return JsonResponse({'status': 'error', 'message': 'Account is not active or email not verified'}, status=400)

    if not user.is_active: user.is_active = True; user.save()
    auth_token = Token.objects.create(user=user, expires_at=timezone.now() + datetime.timedelta(days=1))
    refresh_token = Token.objects.create(user=user, is_refresh_token=True, expires_at=timezone.now() + datetime.timedelta(days=7))
    auth_token.refresh_from_db()
    refresh_token.refresh_from_db()

    return JsonResponse({'status': 'ok', 'auth_token': auth_token.token, 'refresh_token': refresh_token.token,
                         'auth_token_expires_at': auth_token.expires_at, 'refresh_token_expires_at': refresh_token.expires_at})


def refresh_token(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    refresh_token_value = request.POST.get('refresh_token', '')
    if not refresh_token_value:
        return JsonResponse({'status': 'error', 'message': 'Refresh token is required'}, status=400)

    try:
        refresh_token = Token.objects.get(token=refresh_token_value, is_refresh=True)
    except Token.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid refresh token'}, status=400)
    now = timezone.now()
    if now > refresh_token.expires_at:
        return JsonResponse({'status': 'error', 'message': 'Refresh token has expired'}, status=400)

    user = refresh_token.user
    new_auth_token = Token.objects.create(user=user, expires_at=timezone.now() + datetime.timedelta(days=1))
    new_refresh_token = Token.objects.create(user=user, is_refresh_token=False, expires_at=timezone.now() + datetime.timedelta(days=7))
    new_auth_token.refresh_from_db()
    new_refresh_token.refresh_from_db()

    return JsonResponse({'status': 'ok', 'auth_token': new_auth_token.token, 'refresh_token': new_refresh_token.token,
                         'auth_token_expires_at': new_auth_token.expires_at, 'refresh_token_expires_at': new_refresh_token.expires_at})
