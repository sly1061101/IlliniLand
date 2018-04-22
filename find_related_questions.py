import math
import sys
import time
import metapy
import pytoml
import os
import shutil
import numpy as np
import queue as Q

class PL2Ranker(metapy.index.RankingFunction):
	"""
	Create a new ranking function in Python that can be used in MeTA.
	"""
	def __init__(self, some_param=1.0):
		self.param = some_param
		# You *must* call the base class constructor here!
		super(PL2Ranker, self).__init__()

	def score_one(self, sd):
		"""
		You need to override this function to return a score for a single term.
		For fields available in the score_data sd object,
		@see https://meta-toolkit.org/doxygen/structmeta_1_1index_1_1score__data.html
		"""
		tfn = sd.doc_term_count*math.log(1.0+self.param*sd.avg_dl/float(sd.doc_size),2)
		lamb = float(sd.num_docs)/float(sd.corpus_term_count)
		frac = (tfn*1.0*math.log(tfn*lamb,2)+(math.log(math.e,2))*(1.0/lamb-tfn)+0.5*math.log(2*math.pi*tfn,2))/float(tfn+1.0)
		if lamb<1.0 or tfn<=0:
			return 0
		return sd.query_term_weight*frac*1.0
		#return (self.param + sd.doc_term_count) / (self.param * sd.doc_unique_terms + sd.doc_size)

# if __name__ == '__main__':
# 	cwd = os.getcwd()
# 	file = open("s_query.txt", "r")
# 	s_query = file.read()
# 	file.close()
# 	shutil.rmtree(cwd + '/idx')
# 	idx = metapy.index.make_inverted_index('config.toml')
# 	ranker = PL2Ranker(2.0)
# 	query = metapy.index.Document()
# 	query.content(s_query)
# 	top_docs = ranker.score(idx, query, num_results = 3)
# 	print(top_docs)
# 	f = open('result.txt','w')
# 	for t in top_docs:
# 		f.write(str(t[0]) + '\n')
# 	f.close()



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
	#print (matrix)
	return (matrix[size_x - 1, size_y - 1])

if __name__ == '__main__':
	cwd = os.getcwd()
	file = open("s_query.txt", "r")
	s_query = file.read()
	file.close()

	q = Q.PriorityQueue()

	questions = []
	with open("./cranfield/cranfield.dat") as fp:  
		for cnt, line in enumerate(fp):
			questions.append(line)
			q.put((levenshtein(s_query, line),cnt))
	
	file = open("result.txt", "w")
	cnt = 0
	q.get()
	while cnt < 3 and not q.empty():
		file.write(str(q.get()[1]) + "\n")
		cnt += 1
	file.close()