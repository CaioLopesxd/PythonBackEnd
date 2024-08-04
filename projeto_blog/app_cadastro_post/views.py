from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'posts/home.html')

def cadastro_post(request):
    return render(request, 'posts/cadastro_post.html')

