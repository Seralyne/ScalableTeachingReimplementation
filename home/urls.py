from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.login_user, name="login"),
    path('signup/', views.signup, name="signup"),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('profile/', views.user_profile, name ="user_profile")

]
