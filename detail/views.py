from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from movie.models import Movie


def index(request):
    id = request.GET.get('id')
    print(id)
    movie = Movie.objects.filter(id=id)
    print(movie)
    return render(request, 'detail.html', {'movie': movie[0]})


def book(request):
    id = request.GET.get('id')
    m = Movie.objects.filter(id=id)
    stock = m[0].stock - 1
    print(stock)
    movie = Movie.objects.filter(id=id).update(stock=stock)
    mov = Movie.objects.filter(id=id)
    return render(request, 'detail.html', {'movie': mov[0]})
