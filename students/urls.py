from django.urls import include, path
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from students.views import (
    RegisterStudentViewset, ConfirmStudentViewset,
    LoginView, StudentView, ResetPasswordView,
    PingViewset
)

router = DefaultRouter(trailing_slash=False)
router.register(
    'register', RegisterStudentViewset, basename='register-student')
router.register(
    'confirm', ConfirmStudentViewset, basename='confirm-student')
router.register(
    'ping', PingViewset, basename='ping')


urlpatterns = [
    url(r'', include(router.urls)),
    path(r'profile', StudentView.as_view()),
    path(r'login', LoginView.as_view()),
    path(r'reset-password', ResetPasswordView.as_view())
]
