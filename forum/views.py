from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from forum.models import Department, Course, Take, Question, Answer, Comment, Student
from django.db.models import F
import datetime
import json
import random

import metapy
from subprocess import call
import os

from django.db import connection

# Create your views here.

# weights for course recommendation
prof_w = 1
overall_w = 1
diff_w = -1
work_w = -1
major_w = 5
rand_w = 1


def recommend_course(request):
	global prof_w
	global overall_w
	global diff_w
	global work_w
	global major_w
	global rand_w

	rand_w = random.uniform(0.6, 1.4)

	rand_prof_w = prof_w * rand_w
	rand_overall_w = overall_w * rand_w
	rand_diff_w = diff_w * rand_w
	rand_work_w = work_w * rand_w
	rand_major_w = major_w * rand_w

	this_user_id = request.user.id

	with connection.cursor() as cursor:
		# find the 10 courses that have the highest score
		cursor.execute("""DROP VIEW  IF EXISTS score_table;""");
		cursor.execute(
			"""CREATE VIEW score_table AS \
				(SELECT course_id, (%s * AVG(professor_score) + %s * AVG(overall_score) \
									+ %s * AVG(difficulty_score) + %s * AVG(workload_score) + %s) AS score \
				FROM forum_comment \
				WHERE (SELECT DISTINCT department_id \
						FROM forum_student \
						WHERE user_id = %s) \
					= \
						(SELECT DISTINCT department_id \
						FROM forum_course, forum_department \
						WHERE forum_comment.course_id = forum_course.id AND forum_course.department_id = forum_department.id) \
				GROUP BY course_id) \
				UNION \
				(SELECT course_id, (%s * AVG(professor_score) + %s * AVG(overall_score) \
									+ %s * AVG(difficulty_score) + %s * AVG(workload_score)) AS score \
				FROM forum_comment \
				WHERE (SELECT COUNT(*) \
						FROM forum_student \
						WHERE user_id = %s) < 1 \
					OR \
						(SELECT DISTINCT department_id \
						FROM forum_student \
						WHERE user_id = %s) \
					<> \
						(SELECT DISTINCT department_id \
						FROM forum_course, forum_department \
						WHERE forum_comment.course_id = forum_course.id AND forum_course.department_id = forum_department.id) \
				GROUP BY course_id)
				UNION
				(SELECT forum_course.id, %s AS score
				FROM forum_course, forum_student
				WHERE forum_student.user_id = %s AND forum_student.department_id = forum_course.department_id AND forum_course.id <> ALL(SELECT course_id FROM forum_comment));"""
				%(rand_prof_w, rand_overall_w, rand_diff_w, rand_work_w, rand_major_w, this_user_id,
				rand_prof_w, rand_overall_w, rand_diff_w, rand_work_w, this_user_id, this_user_id, rand_major_w, this_user_id));

		cursor.execute(
			"""SELECT forum_course.id \
			FROM \
				(SELECT score_table.course_id \
				FROM score_table \
				ORDER BY score DESC \
				LIMIT 9) as s1, forum_course, forum_department \
			WHERE s1.course_id = forum_course.id AND forum_course.department_id = forum_department.id;""");


		result = cursor.fetchall()
		courses = []
		for curr_id in result:
			courses.append(Course.objects.get(id=curr_id[0]))
		context = {}
		context['courses'] = courses

	if request.method == "POST":
		if request.POST.get('good') is not None:
			modify_factor = (1 + rand_w) / 2 + 1
			prof_w = prof_w * modify_factor
			overall_w = overall_w * modify_factor
			diff_w = diff_w * modify_factor
			work_w = work_w * modify_factor
			major_w = major_w * modify_factor
			rand_w = 1
			return HttpResponseRedirect("/user/home/")
		else:
			modify_factor = (1 - rand_w) / 2 + 1
			prof_w = prof_w * modify_factor
			overall_w = overall_w * modify_factor
			diff_w = diff_w * modify_factor
			work_w = work_w * modify_factor
			major_w = major_w * modify_factor
			rand_w = 1
	return render(request, "forum/user/recommend_course.html", context)



def index(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect("/square/")
	else:
		return render(request, "forum/main.html")

def register(request):
	status = "normal"
	if request.method == 'POST':
		username = request.POST['register_email']
		password = request.POST['register_password']
		password_confirm = request.POST['register_password_confirm']
		if password == password_confirm :
			if not (User.objects.filter(username=username).exists()):
				user = User.objects.create_user(username = username, password = password)
				user = authenticate(username = username, password = password)
				login(request, user)
				return HttpResponseRedirect("/")
			else:
				status = "already-exist"
		else:
			status = "password-different"
	return render(request, "forum/register.html", {'status' : status})

def course(request,course_id): # course?course_id=1
	context = {}
	curr_course = Course.objects.get(id=course_id)
	context['course'] = curr_course
	print(curr_course.get_avg_scores)

	res = curr_course.get_avg_scores()
	overall_score = res[0]
	difficulty_score = res[1]
	workload_score = res[2]
	professor_score = res[3]

	context['overall_score'] = overall_score
	context['difficulty_score'] = difficulty_score
	context['workload_score'] = workload_score
	context['professor_score'] = professor_score
	context['take'] = Take.objects.filter(course=curr_course,user=request.user).count() > 0

	questions = Question.objects.filter(course__id=course_id).order_by('-time')
	context['questions'] = questions

	comments = Comment.objects.filter(course__id=course_id).order_by('-time')
	context['comments'] = comments

	return render(request, "forum/course.html",context)

def add_question(request,course_id):
	if request.method == 'POST':
		question_title = request.POST['question_title']
		question_content = request.POST['question_content']
		new_question = Question(title=question_title, content=question_content, course=Course.objects.get(id=course_id),user=request.user,time= datetime.datetime.now())
		new_question.save()
	return HttpResponseRedirect("/course/" + str(course_id))

def add_comment(request,course_id):
	if request.method == 'POST':
		content = request.POST['review_text']
		difficulty = request.POST['difficulty']
		workload = request.POST['workload']
		professor = request.POST['professor']
		overall = request.POST['overall']
		new_comment = Comment(user=request.user, content=content, overall_score=overall, difficulty_score=difficulty, workload_score=workload, professor_score=professor, course=Course.objects.get(id=course_id),time= datetime.datetime.now())
		new_comment.save()
	return HttpResponseRedirect("/course/" + str(course_id))

def user(request):
	return render(request, "forum/user.html")

def home(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect("/")
	else:
		context = {}
		user_id = request.user.id
		courses = []
		for obj in Take.objects.filter(user__id=user_id):
			courses.append(obj.course)
		context['courses'] = courses
		course_id = request.GET.get('course_id')
		if course_id is None:
			questions = Question.objects.filter(course__in=courses)
			context['curr_course'] = None
		else:
			questions = Question.objects.filter(course__id=course_id)
			context['curr_course'] = Course.objects.get(id=course_id)
		context['questions'] = questions.order_by('-time')

		return render(request, "forum/user/home.html", context)

def question(request, question_id):
	context = {}
	question = Question.objects.get(id = question_id)
	answer_set = Answer.objects.filter(question__id = question_id)
	context["question"] = question
	context["answer_set"] = answer_set.order_by('-time')

	question_all = Question.objects.all()

	#Find related questions

	#save questions to file
	f = open('all_questions.txt','w')
	for q in question_all:
		s = q.title + " " + q.content
		s = s.replace('\r', ' ').replace('\n', '')
		doc = metapy.index.Document()
		doc.content(s)
		tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
		tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)
		tok = metapy.analyzers.LowercaseFilter(tok)
		tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)	
		tok = metapy.analyzers.Porter2Filter(tok)	
		tok.set_content(doc.content())	
		tokens = [token for token in tok]	
		s = ""
		for t in tokens:
			s += t + " "
		f.write(s + '\n')
	f.close()

	#save current question title to file
	s = question.title
	s = s.replace('\r', ' ').replace('\n', '')
	doc = metapy.index.Document()
	doc.content(s)
	tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
	tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)
	tok = metapy.analyzers.LowercaseFilter(tok)
	tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)	
	tok = metapy.analyzers.Porter2Filter(tok)	
	tok.set_content(doc.content())	
	tokens = [token for token in tok]	
	s = ""
	for t in tokens:
		s += t + " "
	f_t = open('s_query_title.txt','w')
	f_t.write(s)
	f_t.close()

	#save current question content to file
	s = question.content
	s = s.replace('\r', ' ').replace('\n', '')
	doc = metapy.index.Document()
	doc.content(s)
	tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
	tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)
	tok = metapy.analyzers.LowercaseFilter(tok)
	tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)	
	tok = metapy.analyzers.Porter2Filter(tok)	
	tok.set_content(doc.content())	
	tokens = [token for token in tok]	
	s = ""
	for t in tokens:
		s += t + " "	
	f_c = open('s_query_content.txt','w')
	f_c.write(s)
	f_c.close()

	#call external program to search
	cwd = os.getcwd()
	call(["python", cwd + "/find_related_questions.py"])

	#read search results and pass to front end
	related = []
	with open("result.txt") as fp:
		for cnt, line in enumerate(fp):
			related.append(int(line))
	related_questions = []
	for num in related:
		related_questions.append(question_all[num])

	context["related_questions"] = related_questions

	return render(request, "forum/question.html", context)

def new_answer(request, question_id):
	new_answer = Answer(content = request.POST["new_answer"], question = Question.objects.get(id = question_id), user = request.user)
	new_answer.save()
	return HttpResponseRedirect("/question/" + str(question_id) + "/")

def profile(request):
    context = {"user":request.user}
    student = Student.objects.filter(user = request.user)
    if student:
        context['student'] = student[0]
    else:
        context['student'] = None
    return render(request, "forum/user/profile.html", context)

def edit_profile(request):
    if request.method == 'POST':
        student = Student.objects.filter(user = request.user)
        if student:
            student = Student.objects.get(user = request.user)
            student.department = Department.objects.get(name = request.POST['major'])
            student.name = request.POST['name']
            student.bio = request.POST['bio']
        else:
            student = Student.objects.filter(user = request.user)
            student = Student(department = Department.objects.get(name = request.POST['major']), user = request.user, name = request.POST['name'], start_date = "2000-01-01", end_data = "2000-01-01", bio = request.POST['bio'])
        student.save()
        if request.POST['register_password'] == request.POST['register_password_confirm'] and request.POST['register_password']:
            user = request.user
            request.user.set_password(request.POST['register_password'])
            request.user.save()
            login(request, user)
        return HttpResponseRedirect("/user/profile/")
    context = {"user":request.user}
    student = Student.objects.filter(user = request.user)
    if student:
        context['student'] = student[0]
    else:
        context['student'] = None
    return render(request, "forum/user/edit_profile.html", context)

def addCourse(request):
	context = {}
	status = 'normal'
	if request.method == 'POST':
		department_name = request.POST['subject']
		course_number = request.POST['course_number']
		context['course_add'] = department_name + str(course_number)
		with connection.cursor() as cursor:
			cursor.execute("""SELECT id
				FROM forum_course
				WHERE number = '%s'
				AND department_id = (SELECT id FROM forum_department WHERE name = '%s');"""%(course_number, department_name))
			result = cursor.fetchall()
			if result:
				course_id = result[0][0]
				user_id = request.user.id
				cursor.execute("SELECT * FROM forum_take WHERE course_id = %s AND user_id = %s;"%(course_id, user_id))
				result2 = cursor.fetchall();
				if not result2 :
					cursor.execute("INSERT INTO forum_take(course_id, user_id) VALUES (%s, %s);"%(course_id, user_id))
					status = 'success'
				else:
					status = 'already-exist'
			else:
				status = 'not-exist'
	current_user = request.user
	with connection.cursor() as cursor:
		cursor.execute("SELECT id FROM auth_user WHERE username = '%s';"%(current_user))
		result = cursor.fetchall()
		user_id = result[0][0]
		cursor.execute("SELECT course_id FROM forum_take WHERE user_id = '%s';"%(user_id))
		result = cursor.fetchall()
		course_taken = []
		for r in result:
			course_id = r[0]
			cursor.execute("""SELECT name, number
				FROM forum_department d,forum_course c
				WHERE c.id = '%s'
				AND c.department_id = d.id;"""%(course_id))
			result2 = cursor.fetchall()
			course_taken.append((result2[0][0] + " " + str(result2[0][1]),course_id))
	context['course_taken'] = course_taken
	context['status'] =  status
	return render(request, "forum/user/addCourse.html", context)

def subscribe_course(request, course_id):
	if request.method == 'GET':
		target = Take.objects.filter(user=request.user,course=Course.objects.get(id=course_id))
		target[0].delete()
		return HttpResponseRedirect("/course/" + str(course_id) + "/")
	elif request.method == 'POST':
		Take(user=request.user,course=Course.objects.get(id=course_id)).save()
		return HttpResponseRedirect("/course/" + str(course_id) + "/")

def delete_course(request, course_id):
	with connection.cursor() as cursor:
		cursor.execute("DELETE FROM forum_take WHERE user_id = %s AND course_id = %s;"%(request.user.id, course_id))
	return HttpResponseRedirect("/user/home/")


def square(request):
	context = {}
	questions = Question.objects.all().order_by('-time')
	context['questions'] = questions
	return render(request, "forum/square.html",context)

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

# view for testing template system
def template_test(request):
	var_test = [1, 2, 3, 4, 5];
	context = {'var_test': var_test}
	return render(request, "forum/template_test.html", context)


def fuzzy_search(term, choices):
	result = process.extract(term, choices, limit = 6)
	return [i[0] for i in result] #no need the point

def search(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect("/login/")
	context={}
	searchtype = request.POST.get("search_type")
	keyword = request.POST.get("search_string")
	courses = []
	questions = []
	if searchtype == "course":
		# with connection.cursor() as cursor:
		# 	cursor.execute("""SELECT CONCAT(name, number)
		# 		FROM forum_course c,forum_department d
		# 		WHERE c.department_id = d.id
		# 		""")
		# 	result = cursor.fetchall()
		# 	course = fuzzy_search(keyword,result)

		str_course_dictionary = {}
		course_str_list = []
		all_courses = Course.objects.all()
		for course in all_courses:
			course_str = course.to_string()
			course_str_list.append(course_str)
			str_course_dictionary[course_str]=course
		courses_str = process.extract(keyword, course_str_list, limit = 6)
		for s in courses_str:
			# print("score: "+str(s[1]))
			courses.append(str_course_dictionary[s[0]])


	elif searchtype == "question":
		str_question_dictionary = {}
		question_str_list = []
		all_questions = Question.objects.all()
		for question in all_questions:
			question_str = question.title
			question_str_list.append(question_str)
			str_question_dictionary[question_str]=question
		question_str = process.extract(keyword, question_str_list, limit = 6)
		for s in question_str:
			# print("score: "+str(s[1]))
			questions.append(str_question_dictionary[s[0]])
	context['courses'] = courses
	context['questions'] = questions
	return render(request, "forum/search.html", context)
