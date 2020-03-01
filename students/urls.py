from django.urls import include, path
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from students.views import (
    RegisterStudentViewset, ConfirmStudentViewset,
    LoginStudentView, LogoutStudentView, StudentView
)

router = DefaultRouter(trailing_slash=False)
router.register('register', RegisterStudentViewset, basename='register-student')
router.register('confirm', ConfirmStudentViewset, basename='confirm-student')

urlpatterns = [
    url(r'', include(router.urls)),
    path(r'student', StudentView.as_view()),
    path(r'login', LoginStudentView.as_view()),
    path(r'logout', LogoutStudentView.as_view())
]
