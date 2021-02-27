"""crowdsourcing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from home import views
from django.views.generic.base import RedirectView
from home.admin import my_adminsite

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/', my_adminsite.urls),

    path('', views.homeView.as_view(), name='home'),
    path('gh/', views.egg, name='egg'),
    path('register/', views.registerView.as_view(), name="register"),
    path('register_verif/', views.register_verif, name='register_verif'),
    path('login/', views.loginView.as_view(), name='login'),
    # path('profile/<userId>', views.profile, name='profile'),
    path('profile/', views.profileView.as_view(), name='profile'),
    path('logout/', views.logout, name='logout'),
    # path('private/', views.privateView.as_view(), name='private'),
    # path('uploadTestdata', taskviews.uploadTestdata, name='uploadTestdata'),
    # path('search', include('haystack.urls')),
    path('upload/', views.upload, name='upload'),
    # path('uploadfile/', views.uploadfile, name='uploadfile'),
    path('wordnumbers/', views.wordnumbers, name='wordnumbers'),
    path('cancelIt/', views.cancelIt, name='cancelIt'),
    path('task/<taskId>', views.task, name='task'),
]
