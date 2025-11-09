import datetime
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from tabibi_models.models import User, Token


def _create_auth_and_refresh_tokens(user):
    Token.objects.filter(user=user).delete()
    auth_token    = Token.objects.create(user=user, is_refresh=False, expires_at=timezone.now() + datetime.timedelta(days=1))
    refresh_token = Token.objects.create(user=user, is_refresh=True , expires_at=timezone.now() + datetime.timedelta(days=7))
    auth_token.refresh_from_db()
    refresh_token.refresh_from_db()
    return auth_token, refresh_token


@csrf_exempt
def register_view(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    body = json.loads(request.body)
    email = body.get('email', '').lower()
    password1 = body.get('password1', '')
    password2 = body.get('password2', '')
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

        print(222, (now - existing_user.created_at).total_seconds())
        if abs(now - existing_user.created_at).total_seconds() > (24*60*60):
            existing_user.delete()
            existing_user = None
    if existing_user:
        return JsonResponse({'status': 'error', 'message': 'Email already registered'}, status=400)
    new_user = User.objects.create(email=email, is_active=False)
    new_user.set_password(password1)
    new_user.save()
    return JsonResponse({'status': 'ok'})


@csrf_exempt
def get_token_view(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    body = json.loads(request.body)
    email = body.get('email', '').lower()
    password = body.get('password', '')
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
    auth_token, refresh_token = _create_auth_and_refresh_tokens(user)
    return JsonResponse({'status': 'ok', 'auth_token': auth_token.token, 'refresh_token': refresh_token.token,
                         'auth_token_expires_at': auth_token.expires_at, 'refresh_token_expires_at': refresh_token.expires_at})


@csrf_exempt
def refresh_token_view(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    body = json.loads(request.body)
    refresh_token_value = body.get('refresh_token', '')
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
    new_auth_token, new_refresh_token = _create_auth_and_refresh_tokens(user)
    return JsonResponse({'status': 'ok', 'auth_token': new_auth_token.token, 'refresh_token': new_refresh_token.token,
                         'auth_token_expires_at': new_auth_token.expires_at, 'refresh_token_expires_at': new_refresh_token.expires_at})


def get_current_info_view(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)
    refresh_token = Token.objects.filter(user=user, is_refresh=True).order_by('-expires_at').first() if Token.objects.filter(user=user, is_refresh=True).exists() else None
    id_scan_base64 = ''
    if user.id_scan and hasattr(user.id_scan, 'read'):
        import base64
        id_scan_content = user.id_scan.read()
        id_scan_base64 = base64.b64encode(id_scan_content).decode('utf-8')
    user_info = {
        'id'           : user.id,
        'email'        : user.email,
        'first_name'   : user.first_name,
        'last_name'    : user.last_name,
        'full_name'    : user.full_name,
        'user_type'    : user.user_type,
        'is_active'    : user.is_active,
        'id_number'    : user.id_number,
        'refresh_token': refresh_token.token if refresh_token else None,
        'refresh_token_expires_at': refresh_token.expires_at if refresh_token else None,
        'id_scan_base64': id_scan_base64,
    }
    return JsonResponse({'status': 'ok', 'user': user_info})


@csrf_exempt
def logout_view(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    user = request.user
    Token.objects.filter(user=user).delete()
    return JsonResponse({'status': 'ok'})


@csrf_exempt
def update_info_view(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)
    if request.headers.get('Content-Type', '') == 'application/json':
        try: body = json.loads(request.body)
        except json.JSONDecodeError: return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    else: body = {}
    id_scan = request.FILES.get('id_scan')
    id_scan_base64 = body.get('id_scan_base64', '').strip()
    id_scan_bytes = None
    if id_scan_base64:
        import base64
        id_scan_bytes = base64.b64decode(id_scan_base64)
    id_number = body.get('id_number', '').strip()
    first_name = body.get('first_name', '').strip()
    last_name = body.get('last_name', '').strip()

    if first_name   : user.first_name = first_name
    if last_name    : user.last_name  = last_name
    if id_number    : user.id_number  = id_number
    if id_scan      : user.id_scan    = id_scan
    if id_scan_bytes: user.id_scan = SimpleUploadedFile('id_scan.png', id_scan_bytes)
    user.save()
    return JsonResponse({'status': 'ok'})
