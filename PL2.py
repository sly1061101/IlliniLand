import math
import sys
import time
import metapy
import pytoml
import os
import shutil

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

if __name__ == '__main__':
	cwd = os.getcwd()
	file = open("s_query.txt", "r")
	s_query = file.read()
	file.close()
	shutil.rmtree(cwd + '/idx')
	idx = metapy.index.make_inverted_index('config.toml')
	ranker = PL2Ranker(3.0)
	query = metapy.index.Document()
	query.content(s_query)
	top_docs = ranker.score(idx, query, num_results = 3)
	print(top_docs)
	f = open('result.txt','w')
	for t in top_docs:
		f.write(str(t[0]) + '\n')
	f.close()