from django.urls import include
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from firstaid.views import FirstAidTipView

router = DefaultRouter(trailing_slash=False)
router.register('tip', FirstAidTipView, basename='firstaid-tip')


urlpatterns = [
    url(r'', include(router.urls)),
]
