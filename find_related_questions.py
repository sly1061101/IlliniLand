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
	file = open("s_query.txt", "r")
	s_query = file.read()
	file.close()

	doc = metapy.index.Document()
	doc.content(s_query)
	tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)	
	tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)	
	tok = metapy.analyzers.LowercaseFilter(tok)	
	tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)	
	tok = metapy.analyzers.Porter2Filter(tok)	
	tok.set_content(doc.content())	
	tokens = [token for token in tok]	
	s_query = ""	
	for t in tokens:	
		s_query += t + " "

	q = Q.PriorityQueue()

	questions = []
	with open("all_questions.txt") as fp:  
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
			print(line)
			q.put((levenshtein(s_query, line),cnt))
	
	file = open("result.txt", "w")
	cnt = 0
	q.get()
	while cnt < 3 and not q.empty():
		file.write(str(q.get()[1]) + "\n")
		cnt += 1
	file.close()