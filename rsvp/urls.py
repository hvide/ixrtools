from django.urls import path
from .views import HomePageView, SearchPathPageView, get_path, create_path

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('search_path.html', SearchPathPageView.as_view(), name="search_path"),
    path('results.html', get_path, name="get_path"),
    path('create_path.html', create_path, name="create_path")
]