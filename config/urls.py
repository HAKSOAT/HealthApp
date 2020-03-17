"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from utils.constants import student_base_url, health_centre_base_url, \
    firstaid_base_url
from students.views import LogoutView

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


urlpatterns = [
    path(student_base_url, include('students.urls')),
    path(health_centre_base_url, include('healthcentre.urls')),
    path(firstaid_base_url, include('firstaid.urls')),
    path('api/v1/logout', LogoutView.as_view()),
    path(r'api/v1/swagger', swagger_schema_view.with_ui(
            'swagger', cache_timeout=0), name='schema-swagger-ui')
]
