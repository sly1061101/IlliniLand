import math
import sys
import time
import metapy
import pytoml
import os
import shutil
import numpy as np
import queue as Q
from querytexts import Query
import operator

if __name__ == '__main__':
	cwd = os.getcwd()
	file = open("s_query_title.txt", "r")
	s_query_title = file.read()
	file.close()

	file = open("s_query_content.txt", "r")
	s_query_content = file.read()
	file.close()

	q = Query("all_questions_title.txt")
	results_t2t = q.search_with_all_docs(s_query_title)
	q = Query("all_questions_content.txt")
	
	results_t2c = q.search_with_all_docs(s_query_title)
	results_c2c = q.search_with_all_docs(s_query_content)

	possible_filenames = set().union(results_t2t.keys(), results_t2c.keys(), results_c2c.keys())
	results = {}
	for i in possible_filenames:
		if i not in results_t2t.keys():
			results_t2t[i] = 0
		if i not in results_t2c.keys():
			results_t2c[i] = 0
		if i not in results_c2c.keys():
			results_c2c[i] = 0
		#give different weights for similarities between title with title, title with content and content with content
		results[i] = results_t2t[i]*3 + results_t2c[i]*1 + results_c2c[i]*0.25

	results = sorted(results.items(), key=operator.itemgetter(1))
	results.reverse()

	print(results)
	# for i, r in enumerate(results):
	# 	results[i] = (r[0], r[1] - results[len(results)-1][1])

	file = open("result.txt", "w")
	cnt = 0
	while cnt < 5 and results[cnt][1] > 0:
		file.write(str(results[cnt][0]) + "\n")
		cnt += 1
	file.close()