from django.urls import include, path
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from students.views import (
    RegisterStudentViewset, ConfirmStudentViewset,
    LoginStudentView, LogoutStudentView, StudentView,
)

swagger_schema_view = get_schema_view(
   openapi.Info(
      title="Students API",
      default_version='v1',
      description="Provides end points for the students API",
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(),
   authentication_classes=()
)


router = DefaultRouter(trailing_slash=False)
router.register('register', RegisterStudentViewset, basename='register-student')
router.register('confirm', ConfirmStudentViewset, basename='confirm-student')


urlpatterns = [
    url(r'', include(router.urls)),
    path(r'student', StudentView.as_view()),
    path(r'login', LoginStudentView.as_view()),
    path(r'logout', LogoutStudentView.as_view()),
    path(r'swagger', swagger_schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
]
