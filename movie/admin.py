from django.contrib import admin
from .models import Movie
import movie.models


# Register your models here.


class MovieAdmin(admin.ModelAdmin):
    list_display = ('ID', 'title', 'url', 'grade', 'duration')


admin.site.register(Movie)
