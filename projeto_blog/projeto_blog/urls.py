from django.urls import path
from app_cadastro_post import views

urlpatterns = [
    path("", views.home, name="home"),
    path("cadastro_post/", views.cadastro_post, name="cadastro_post"),
]
