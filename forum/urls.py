"""illiniland URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
	path('', views.index),
	path('login/', auth_views.login),
	path('logout/', auth_views.logout),
	path('register/', views.register),
    path('user/', views.user),
    path('profile/', views.profile),
    path('edit_profile/', views.edit_profile),
    path('import_data/', views.import_data),
    path('course/', views.course),
    path('initial_demo/', views.initial_demo),
    path('template_test/', views.template_test),
]