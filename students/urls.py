from django.urls import include
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from students.views import RegisterStudentViewset, ConfirmStudentViewset, LoginStudentViewset

router = DefaultRouter(trailing_slash=False)
router.register('register', RegisterStudentViewset, basename='register-student')
router.register('confirm', ConfirmStudentViewset, basename='confirm-student')
router.register('login', LoginStudentViewset, basename='login-student')

urlpatterns = [
    url(r'', include(router.urls)),
]
