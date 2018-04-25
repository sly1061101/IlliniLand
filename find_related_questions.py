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

if __name__ == '__main__':
	cwd = os.getcwd()
	file = open("s_query_title.txt", "r")
	s_query_title = file.read()
	file.close()

	file = open("s_query_content.txt", "r")
	s_query_content = file.read()
	file.close()

	q = Query("all_questions.txt")
	results = q.search_with_all_docs(s_query_title + " " + s_query_content)

	file = open("result.txt", "w")
	cnt = 1
	while cnt < 4 and results[cnt][1] > 0:
		file.write(str(results[cnt][0]) + "\n")
		cnt += 1
	file.close()