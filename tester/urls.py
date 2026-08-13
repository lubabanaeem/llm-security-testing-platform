from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("reports/", views.reports, name="reports"),
    path("attack_library/", views.attack_library, name="attack_library"),
    path("history/", views.history, name="history"),
]
