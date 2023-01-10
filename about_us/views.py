from django.shortcuts import render
from .models import FrontImage
from movie.models import Movie

# Create your views here.

from django.http import HttpResponse


def index(request):
    ids = FrontImage.objects.all()
    list = []
    for i in ids:
        list.append(i.FID)
    print(list)
    movies = Movie.objects.filter(id__in=list)
    print(movies[0].title)
    return render(request, 'about_us.html', {'movies0': movies[0], 'movies1': movies[1], 'movies2': movies[2]})
