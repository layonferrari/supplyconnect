from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from access_control import views as access_views  # ← NOVA LINHA

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("login/", RedirectView.as_view(pattern_name='accounts:home_choice'), name='login'),
    path("logout/", RedirectView.as_view(pattern_name='accounts:logout'), name='logout_redirect'),
    path("admin-login/", access_views.admin_login, name='admin_login'),  # ← NOVA LINHA (sem idioma!)
]

urlpatterns += i18n_patterns(
    path("", include("accounts.urls")),
    path("adminpanel/", include("adminpanel.urls")),
    path("admin-panel/", include("access_control.urls")),
    path("home/", RedirectView.as_view(pattern_name='accounts:home_choice'), name='home'),
)