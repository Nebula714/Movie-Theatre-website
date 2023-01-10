from django.shortcuts import render
from .models import Movie


# Create your views here.


def index(request):
    title = request.GET.get('title')
    if not title:
        movie_all = Movie.objects.all()
    else:
        movie_all = Movie.objects.filter(title__icontains=title)
    type = request.GET.get('type')
    #movie_all = Movie.objects.all()
    return render(request, 'movies.html', {'movies': movie_all})
