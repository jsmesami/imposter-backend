from rest_framework import routers

from imposter.api.views import BureauViewSet, PosterSpecViewSet, PosterViewSet

router = routers.SimpleRouter()


router.register(r'bureau', BureauViewSet)
router.register(r'spec', PosterSpecViewSet)
router.register(r'poster', PosterViewSet)
