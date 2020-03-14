from django.urls import include, path
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from students.views import LoginView

router = DefaultRouter(trailing_slash=False)
# router.register(
    # 'register', RegisterStudentViewset, basename='register-student')


urlpatterns = [
    url(r'', include(router.urls)),
    path(r'login', LoginView.as_view()),
]
