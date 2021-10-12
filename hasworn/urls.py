"""hasworn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

from hasworn.views import Home, All, Login, Logout
from hasworn.clothing.views import CreateWearing, DeleteWearing, CreateClothing


urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', Login.as_view(), name = 'login'),
    path('logout/', Logout.as_view(), name = 'logout'),

    path(
        '',
        Home.as_view(),
        name = 'homepage'
    ),
    path(
        'all/',
        All.as_view(),
        name = 'all-clothing',
    ),

    path(
        'wearing/',
        CreateWearing.as_view(),
        name = 'create-wearing',
    ),
    path(
        'wearing/<pk>',
        DeleteWearing.as_view(),
        name = 'delete-wearing',
    ),
    path(
        'clothing/',
        CreateClothing.as_view(),
        name = 'create-clothing',
    ),
]
