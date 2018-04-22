from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Department(models.Model):
	name = models.CharField(max_length=100)

class Student(models.Model):
	department = models.ForeignKey(Department, on_delete=models.CASCADE)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	start_date = models.DateField()
	end_data = models.DateField()
	bio = models.TextField()

class Course(models.Model):
	number = models.IntegerField()
	title = models.CharField(max_length=100)
	department = models.ForeignKey(Department, on_delete=models.CASCADE)
	description = models.TextField()
	def get_number_comments(self):
		all_comments = Comment.objects.filter(course_id=self.id)
		return len(all_comments)
	
	def get_avg_scores(self):
		all_comments = Comment.objects.filter(course_id=self.id)
		n_comments = len(all_comments)
		total_overall = 0
		total_difficulty = 0
		total_workload = 0
		total_professor = 0
		for comment in all_comments:
			total_overall += comment.overall_score
			total_difficulty += comment.difficulty_score
			total_workload += comment.workload_score
			total_professor += comment.professor_score
		if n_comments == 0:
			n_comments = 1
		return (total_overall/n_comments, total_difficulty/n_comments, total_workload/n_comments, total_professor/n_comments)

	def to_string(self):
		str = ""
		str += self.department.name
		str += str(self.number)
		str += self.description
		return str




class Take(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

class Comment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	content = models.TextField(default="")
	overall_score = models.FloatField()
	difficulty_score = models.FloatField()
	workload_score = models.FloatField()
	professor_score = models.FloatField()
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	time = models.DateTimeField(auto_now=True)

class Question(models.Model):
	title = models.CharField(max_length=100)
	content = models.TextField()
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	time = models.DateTimeField(auto_now=True)
	def get_number_answers(self):
		return len(Answer.objects.filter(question__id=self.id))

class Answer(models.Model):
	content = models.TextField()
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	time = models.DateTimeField(auto_now=True)
