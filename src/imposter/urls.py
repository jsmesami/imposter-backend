from django.conf.urls import url, include

from imposter.api import views
from imposter.api.routers import router


urlpatterns = [
    # We are using custom APIRootView instead of DefaultRouter's root view,
    # because we don't want domain in endpoint urls.
    url(r'^api/$', views.APIRootView.as_view(), name='api-root'),
    url(r'^api/', include(router.urls)),
]
