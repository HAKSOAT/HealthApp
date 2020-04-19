from django.urls import include, path
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from students.views import LoginView
from healthcentre.views import PingViewset, StudentView, IoTPingViewset, \
    ws_index, StatisticsView

router = DefaultRouter(trailing_slash=False)
router.register('ping/iot', IoTPingViewset, basename='get-ping-iot')
router.register('ping', PingViewset, basename='get-ping')
router.register('student', StudentView, basename='get-student')
router.register('statistics', StatisticsView, basename='get-statistics')


urlpatterns = [
    url(r'', include(router.urls)),
    path(r'login', LoginView.as_view()),
    path('ws', ws_index, name='index'),
]
