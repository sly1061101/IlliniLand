from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from forum.models import Department, Course
import json

from django.db import connection

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

def course(request):
	return render(request, "forum/course.html")

#view for initial demo
def initial_demo(request):
	if request.method == 'POST':
		# return HttpResponse(request.method.GET[])
		department_ = "'"+request.POST['department']+"'"
		number_ = request.POST['number']
		title_ = "'"+request.POST['title']+"'"
		description_ = "'"+request.POST['description']+"'"

		if request.POST['choice'] == 'insert':
			with connection.cursor() as cursor:
				cursor.execute("INSERT INTO forum_course(number, title, description, department_id) VALUES (%s, %s, %s, (SELECT id FROM forum_department WHERE name = %s));" % (number_, title_, description_, department_))

				cursor.execute("SELECT * FROM forum_course WHERE number=%s AND department_id =  (SELECT id FROM forum_department WHERE name = %s);"%(number_, department_))
				result = cursor.fetchall()
				ret = '<br/>'.join(str(v) for v in result)
				ret = '<p>' + ret + '</p>'

				return HttpResponse("Successfully inserted tuple into DB!" + "<p><a href = '\initial_demo'>Go Back</a></p>" + ret)
		elif request.POST['choice'] == 'query':
			with connection.cursor() as cursor:
				cursor.execute("SELECT * FROM forum_course WHERE number=%s AND department_id =  (SELECT id FROM forum_department WHERE name = %s);"%(number_, department_))
				result = cursor.fetchall()
				ret = '<br/>'.join(str(v) for v in result)
				ret = '<p>' + ret + '</p>'
				return HttpResponse("<p><a href = '\initial_demo'>Go Back</a></p>" + ret)
		elif request.POST['choice'] == 'update':
			with connection.cursor() as cursor:
				cursor.execute("UPDATE forum_course SET title = %s, description = %s WHERE number=%s AND department_id =  (SELECT id FROM forum_department WHERE name = %s);" % (title_, description_, number_, department_))
				
				cursor.execute("SELECT * FROM forum_course WHERE number=%s AND department_id =  (SELECT id FROM forum_department WHERE name = %s);"%(number_, department_))
				result = cursor.fetchall()
				ret = '<br/>'.join(str(v) for v in result)
				ret = '<p>' + ret + '</p>'

				return HttpResponse("Successfully updated tuple in DB!" + "<p><a href = '\initial_demo'>Go Back</a></p>" + ret)
		elif request.POST['choice'] == 'delete':
			with connection.cursor() as cursor:
				cursor.execute("DELETE FROM forum_course WHERE number=%s AND department_id =  (SELECT id FROM forum_department WHERE name = %s);" % (number_, department_))
				
				cursor.execute("SELECT * FROM forum_course WHERE number=%s AND department_id =  (SELECT id FROM forum_department WHERE name = %s);"%(number_, department_))
				result = cursor.fetchall()
				ret = '<br/>'.join(str(v) for v in result)
				ret = '<p>' + ret + '</p>'

				return HttpResponse("Successfully updated tuple in DB!" + "<p><a href = '\initial_demo'>Go Back</a></p>" + ret)
		elif request.POST['choice'] == 'advanced1':
			with connection.cursor() as cursor:
				sql = """SELECT forum_department.name, COUNT(forum_course.id) 
							FROM forum_course, forum_department 
							WHERE forum_course.department_id = forum_department.id 
							GROUP BY forum_department.name"""
				cursor.execute(sql)

				result = cursor.fetchall()
				ret = '<br/>'.join(str(v) for v in result)
				ret = '<p>' + ret + '</p>'

				return HttpResponse("Advanced SQL Query 1:<br/><br/>" + sql + "<br/><br/>Result of Advanced Query 1 (Number of courses provided by every department): " + "<p><a href = '\initial_demo'>Go Back</a></p>" + ret)
		elif request.POST['choice'] == 'advanced2':
			with connection.cursor() as cursor:
				sql = """SELECT d1.name
						FROM
						(SELECT forum_department.name
						FROM forum_course, forum_department
						WHERE (forum_course.department_id = forum_department.id)
						  AND (forum_course.number >= 400)
						  AND (forum_course.number < 500)
						GROUP BY forum_department.name
						HAVING COUNT(forum_course.id) > 15) AS d1
						,
						(SELECT forum_department.name
						FROM forum_course, forum_department
						WHERE (forum_course.department_id = forum_department.id)
						  AND (forum_course.number >= 500)
						  AND (forum_course.number < 600)
						GROUP BY forum_department.name
						HAVING COUNT(forum_course.id) > 15) AS d2
						WHERE d1.name = d2.name"""

				cursor.execute(sql)

				result = cursor.fetchall()
				ret = '<br/>'.join(str(v) for v in result)
				ret = '<p>' + ret + '</p>'
				
				return HttpResponse("Advanced SQL Query 2:<br/><br/>" + sql + "<br/><br/>Result of Advanced Query 2 (Departments which provide both more than 15 400-level courses and 15 500-level courses): " + "<p><a href = '\initial_demo'>Go Back</a></p>" + ret)

	else:
		return render(request, "forum/initial_demo.html")

# A special view for importing data into database. Only used for developing.
def import_data(request):
	if(request.method == 'POST'):
		if request.POST['command'] == 'department':
			with open('./data.json') as json_file:
				data = json.load(json_file)
				for subject in data:
					department = Department(name = subject)
					department.save()
			return HttpResponse("Finish!")
		elif request.POST['command'] == 'course':
			with open('./data.json') as json_file:
				data = json.load(json_file)
				for subject in data:
					for number in data[subject]['courses']:
						title = data[subject]['courses'][number]['course_title']
						description = data[subject]['courses'][number]['description']
						department = Department.objects.get(name=subject)
						course = Course(number=number, title=title, department=department, description=description)
						course.save()
			return HttpResponse("Finish!")	
		else:
			return HttpResponse("Invalid command!")
	else:
		return render(request, "forum/import_data.html")
