"""
Middleware para aplicar automaticamente o idioma preferido do usuário.
"""
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin


class UserLanguageMiddleware(MiddlewareMixin):
    """
    Middleware que aplica o idioma preferido do usuário APENAS quando autenticado.
    Para páginas públicas, NÃO interfere - deixa o LocaleMiddleware funcionar.
    """
    
    def process_request(self, request):
        # CRÍTICO: Não fazer nada se o usuário NÃO estiver autenticado
        # Deixa o LocaleMiddleware padrão do Django gerenciar o idioma
        if not request.user.is_authenticated or request.user.is_anonymous:
            return None  # Não interfere
        
        # Apenas aplica idioma preferido se usuário estiver autenticado
        if hasattr(request.user, 'preferred_language') and request.user.preferred_language:
            language = request.user.preferred_language
            translation.activate(language)
            request.LANGUAGE_CODE = language
    
    def process_response(self, request, response):
        # Adiciona header para não cachear preferências de idioma em páginas autenticadas
        if hasattr(request, 'user') and request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response