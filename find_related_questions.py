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

	# doc = metapy.index.Document()
	# doc.content(s_query_title)
	# tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)	
	# # tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)	
	# # tok = metapy.analyzers.LowercaseFilter(tok)	
	# # tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)	
	# # tok = metapy.analyzers.Porter2Filter(tok)	
	# tok.set_content(doc.content())	
	# tokens = [token for token in tok]	
	# s_query_title = ""	
	# for t in tokens:	
	# 	s_query_title += t + " "

	# file = open("s_query_content.txt", "r")
	# s_query_content = file.read()
	# file.close()

	# doc = metapy.index.Document()
	# doc.content(s_query_content)
	# tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)	
	# # tok = metapy.analyzers.LengthFilter(tok, min=2, max=30)	
	# # tok = metapy.analyzers.LowercaseFilter(tok)	
	# # tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)	
	# # tok = metapy.analyzers.Porter2Filter(tok)	
	# tok.set_content(doc.content())	
	# tokens = [token for token in tok]	
	# s_query_content = ""	
	# for t in tokens:	
	# 	s_query_content += t + " "

	print(s_query_title)

	q = Query("all_questions_title.txt")
	results = q.search_with_all_docs(s_query_title)

	print(results)

	file = open("result.txt", "w")
	cnt = 1
	while cnt < 4 and results[cnt][1] > 0:
		file.write(str(results[cnt][0]) + "\n")
		cnt += 1
	file.close()