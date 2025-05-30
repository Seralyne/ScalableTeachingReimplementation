from django.urls import path
from . import views

urlpatterns = [
    # If webhook caller doesn't support any authentication, a more randomized URL mapping should be used.
    path('achievement/award', views.achievement_webhook, name="index"),
    path('gitlab/receive', views.gitlab_receive, name="gitlab_receive"),
    path('poll_achievements/<str:username>', views.poll_achievements, name="poll_achievements"),
    path('test', views.webhook_test, name="test")
]
