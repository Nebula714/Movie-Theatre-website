"""website URL Configuration

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
from django.urls import path, include
from django.conf.urls import url
import homepage.views
import about_us.views
import admin_movie.views
import movie.views
import detail.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('homepages/', include('homepage.urls')),
    path('about_us/movies', movie.views.index),
    path(r'about_us/movies/detail', detail.views.index),
    path(r'about_us/movies/book', detail.views.book),
    path('about_us/', about_us.views.index),
    path('admin_manage/', admin_movie.views.index),

    url(r'^$', homepage.views.index),
]
