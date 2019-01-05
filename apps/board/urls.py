from django.conf.urls import url
from django.urls import include
from rest_framework_nested import routers

from apps.board.views import BoardViewSet, CategoryViewSet, ThreadViewSet

# Order matters!
router = routers.SimpleRouter()
router.register(r'boards', BoardViewSet)
router.register(r'categories', CategoryViewSet)

boards_router = routers.NestedSimpleRouter(router, r'boards', lookup='board')
boards_router.register(r'threads', ThreadViewSet, base_name='board-threads')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(boards_router.urls)),
]
