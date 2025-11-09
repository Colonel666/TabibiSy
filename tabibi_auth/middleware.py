from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from tabibi_models.models import Token


class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            return self.get_response(request)

        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token_value = auth_header.split('Bearer ')[1].strip()
            try:
                token = Token.objects.select_related('user').get(token=token_value, is_refresh=False)

                if timezone.now() <= token.expires_at: request.user = token.user
                else                                 : request.user = AnonymousUser()
            except Token.DoesNotExist:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()

        response = self.get_response(request)
        return response
