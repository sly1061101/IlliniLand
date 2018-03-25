from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Department(models.Model):
	name = models.CharField(max_length=100)

class Student(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	department = models.ForeignKey(Department, on_delete=models.CASCADE)

class Course(models.Model):
    course_number= models.IntegerField(default=200)
    credit= models.IntegerField(default=10)
    description= models.CharField(max_length=200,default='DEFAULT VALUE')
    gened = ArrayField(models.CharField(max_length=200),null=True)
    depart_name= models.ForeignKey(Department,on_delete=models.CASCADE)
    prof_name= models.ForeignKey(Professor,on_delete=models.CASCADE)
    difficulty=models.FloatField(default=10)
    overall_score = models.FloatField()
    workload=models.FloatField(default=200)
    forum_id=models.IntegerField(default=250)

class Forum(models.Model):
	FIN = models.IntegerField(primary_key = True)
	course = models.OneToOneField(Course, on_delete=models.CASCADE)

class Take(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)

class Comment(models.Model):
	CID = models.IntegerField(primary_key = True)
	title = models.CharField(max_length=100)
	content = models.TextField()
	overall_score = models.FloatField()
	difficulty = models.FloatField()
	workload = models.FloatField()
	course = models.ForeignKey(Course, on_delete=models.CASCADE)

class Make(models.Model):
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

class Professor(models.Model):
	PIN = models.IntegerField(primary_key = True)
	name = models.CharField(max_length=100)
	department = models.ForeignKey(Department, on_delete=models.CASCADE)

class Instruct(models.Model):
	professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)

class Question(models.Model):
	QIN = models.IntegerField(primary_key = True)
	title = models.CharField(max_length=100)
	content = models.TextField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	forum = models.ForeignKey(Forum, on_delete=models.CASCADE)

class Answer(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	AIN = models.IntegerField()
	content = models.TextField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)	
