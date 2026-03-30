from django.urls import path
from . import views

app_name = "spots"

urlpatterns = [
    path("", views.home, name="home"),
    path("spots/create/", views.spot_create, name="spot_create"),
    path("spots/<int:pk>/", views.spot_detail, name="spot_detail"),
    path("spots/<int:pk>/edit/", views.spot_edit, name="spot_edit"),
    path("spots/<int:pk>/delete/", views.spot_delete, name="spot_delete"),
    path("spots/<int:pk>/like/", views.spot_like, name="spot_like"),
    path("spots/<int:pk>/bookmark/", views.spot_bookmark, name="spot_bookmark"),
    path("spots/search/", views.spot_search, name="spot_search"),
]
