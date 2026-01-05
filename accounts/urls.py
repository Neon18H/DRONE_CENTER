from django.urls import path

from .views import LoginRedirectView, LoginView, UserLogoutView

urlpatterns = [
    path("", LoginView.as_view(), name="login"),
    path("redirect/", LoginRedirectView.as_view(), name="login-redirect"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]
