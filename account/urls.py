from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'account'
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('registrate/', views.registrate, name='registrate'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),

]