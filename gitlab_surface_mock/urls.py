from django.urls import path
from . import views

urlpatterns = [
    # If webhook caller doesn't support any authentication, a more randomized URL mapping should be used.
    path('api/v4/projects/<int:id>/jobs', views.index, name="index"),
    path('pipeline_output',views.pipeline_webhook_output, name="pipeline_output")
]
