from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.auth_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),

]