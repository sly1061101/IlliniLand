import math
import sys
import time
import metapy
import pytoml
import os
import shutil
import numpy as np
import queue as Q

def levenshtein(seq1, seq2):  
	size_x = len(seq1) + 1
	size_y = len(seq2) + 1
	matrix = np.zeros ((size_x, size_y))
	for x in range(size_x):
		matrix [x, 0] = x
	for y in range(size_y):
		matrix [0, y] = y

	for x in range(1, size_x):
		for y in range(1, size_y):
			if seq1[x-1] == seq2[y-1]:
				matrix [x,y] = min(
					matrix[x-1, y] + 1,
					matrix[x-1, y-1],
					matrix[x, y-1] + 1
				)
			else:
				matrix [x,y] = min(
					matrix[x-1,y] + 1,
					matrix[x-1,y-1] + 1,
					matrix[x,y-1] + 1
				)
	return (matrix[size_x - 1, size_y - 1])


if __name__ == '__main__':
	cwd = os.getcwd()
	file = open("s_query_title.txt", "r")
	s_query_title = file.read()
	file.close()

	doc = metapy.index.Document()
	doc.content(s_query_title)
	tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)	
	tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)	
	tok = metapy.analyzers.LowercaseFilter(tok)	
	tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)	
	tok = metapy.analyzers.Porter2Filter(tok)	
	tok.set_content(doc.content())	
	tokens = [token for token in tok]	
	s_query_title = ""	
	for t in tokens:	
		s_query_title += t + " "

	file = open("s_query_content.txt", "r")
	s_query_content = file.read()
	file.close()

	doc = metapy.index.Document()
	doc.content(s_query_content)
	tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)	
	tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)	
	tok = metapy.analyzers.LowercaseFilter(tok)	
	tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)	
	tok = metapy.analyzers.Porter2Filter(tok)	
	tok.set_content(doc.content())	
	tokens = [token for token in tok]	
	s_query_content = ""	
	for t in tokens:	
		s_query_content += t + " "
 
	q = Q.PriorityQueue()

	all_questions_title = []
	with open("all_questions_title.txt") as fp:  
		for cnt, line in enumerate(fp):
			doc = metapy.index.Document()
			doc.content(line)
			tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)	
			tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)	
			tok = metapy.analyzers.LowercaseFilter(tok)	
			tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)	
			tok = metapy.analyzers.Porter2Filter(tok)	
			tok.set_content(doc.content())	
			tokens = [token for token in tok]	
			line = ""	
			for t in tokens:	
				line += t + " "
			all_questions_title.append(line)


	all_questions_content = []
	with open("all_questions_content.txt") as fp:  
		for cnt, line in enumerate(fp):
			doc = metapy.index.Document()
			doc.content(line)
			tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)	
			tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)	
			tok = metapy.analyzers.LowercaseFilter(tok)	
			tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)	
			tok = metapy.analyzers.Porter2Filter(tok)	
			tok.set_content(doc.content())	
			tokens = [token for token in tok]	
			line = ""	
			for t in tokens:	
				line += t + " "
			all_questions_content.append(line)

	distance_title = []
	distance_content = []
	for i in range(0, len(all_questions_title)):
		distance_title.append(levenshtein(s_query_title, all_questions_title[i] + " " + all_questions_content[i]))
		distance_content.append(levenshtein(s_query_content, all_questions_title[i] + " " + all_questions_content[i]))

	for i in range(0, len(distance_title)):
		q.put((distance_title[i], i))
		# if distance_content[i] > 20*distance_title[i]:
		# 	q.put((distance_title[i] + distance_content[i]/10, i))
		# else:
		# 	q.put((distance_title[i], i))

	file = open("result.txt", "w")
	cnt = 0
	score = q.get()
	while cnt < 3 and not q.empty():
		print(score)
		if score[0] > 0 and score[0] < 20:
			file.write(str(score[1]) + "\n")
		cnt += 1
		score = q.get()
	file.close()