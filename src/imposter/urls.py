from django.conf.urls import url, include

from imposter.api.routers import router


urlpatterns = [
    url(r'^api/', include(router.urls)),
]
