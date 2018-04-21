from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.

def index(request):
	if request.user.is_authenticated: 
		return render(request, "forum/home.html")
	else:
		return render(request, "forum/main.html")

def register(request):
	if request.method == 'POST':
		username = request.POST['register_email']
		password = request.POST['register_password']
		if not (User.objects.filter(username=username).exists()):
			user = User.objects.create_user(username = username, password = password)
			user = authenticate(username = username, password = password)
			login(request, user)
			return HttpResponseRedirect("/")
		else:
			return HttpResponse("User: " + username + " already exist!")
	else:
		return render(request, "forum/register.html")

def user(request):
	return render(request, "forum/user.html")

def profile(request):
	return render(request, "forum/profile.html")

def edit_profile(request):
	return render(request, "forum/edit_profile.html")

def home(request):
	queryset_list =Post.objects.active()
	query = request.GET.get("p")
	if query:
		queryset_list=queryset_list.filter(title_icontains= query)

	return render(request, "forum/home.html")

def course(request):
	return render(request, "forum/course.html")
