from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "learning"

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", views.home, name="home_compat"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="learning/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("my-profiles/", views.my_profiles, name="my_profiles"),
    path("dashboard/<int:profile_id>/", views.dashboard, name="dashboard"),
    path("ask-tutor/<int:profile_id>/", views.ask_tutor, name="ask_tutor"),
    path("certificate/<int:profile_id>/", views.certificate, name="certificate"),
    path("language/<int:language_id>/profile/<int:profile_id>/", views.language_detail, name="language_detail"),
    path(
        "language/<int:language_id>/profile/<int:profile_id>/lesson/<int:lesson_id>/",
        views.lesson_detail,
        name="lesson_detail",
    ),
]
