from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("reports/", views.reports_list_view, name="reports_list"),
    path(
        "reports/<int:evaluation_id>/",
        views.single_report_detail_view,
        name="report_detail",
    ),
    path("attack_library/", views.attack_library, name="attack_library"),
]
