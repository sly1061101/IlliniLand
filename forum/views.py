from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from forum.models import Department, Course
import json

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

def import_data(request):
	if(request.method == 'POST'):
		if request.POST['command'] == 'department':
			with open('/Users/liuyi/Desktop/data.json') as json_file:
				data = json.load(json_file)
				for subject in data:
					department = Department(name = subject)
					department.save()
		elif request.POST['command'] == 'course':
			with open('/Users/liuyi/Desktop/data.json') as json_file:
				data = json.load(json_file)
				for subject in data:
					for number in data[subject]['courses']:
						title = data[subject]['courses'][number]['course_title']
						department = Department.objects.get(name=subject)
						course = Course(number=number, title=title, department=department, overall_score=0, difficulty=0, workload=0)
						course.save()
		return HttpResponse("success!")
	else:
		return render(request, "forum/import_data.html")