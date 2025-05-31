from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="courses"),
    path('<str:id>', views.course, name="course"),
]
