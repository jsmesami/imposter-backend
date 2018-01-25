from rest_framework import routers

from imposter.api.viewsets import BureauViewSet, PosterSpecViewSet, PosterViewSet

router = routers.DefaultRouter()


router.register(r'bureau', BureauViewSet)
router.register(r'spec', PosterSpecViewSet)
router.register(r'poster', PosterViewSet)
