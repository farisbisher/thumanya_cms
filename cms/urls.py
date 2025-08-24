from django.urls import path, include
from . import views
from rest_framework import routers
from .views import ProgramViewSet, CategoryViewSet

app_name = 'cms'

router = routers.DefaultRouter()
router.register(r'programs', ProgramViewSet, basename='programs')
router.register(r'categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path('', views.index, name='index'),
    path('', include(router.urls)),
]