import buildindex
import re
import operator

class Query:

	def __init__(self, filename):
		self.filename = filename
		self.index = buildindex.BuildIndex(self.filename)
		self.invertedIndex = self.index.totalIndex
		self.regularIndex = self.index.regdex

	def query_term_frequency_inversed_document_frequency(self, query):
		pattern = re.compile('[\W_]+')
		query_to_terms = query.lower();
		query_to_terms = pattern.sub(' ', query_to_terms)
		re.sub(r'[\W_]+','', query_to_terms)

		#query_to_term = ["word1", "word2", ...]
		query_to_terms = query_to_terms.split()

		#query_word_count = {"word1": frequency of word1, ...}
		#words are those that the query contains
		query_word_count = {}
		for word in query_to_terms:
			if word in query_word_count.keys():
				query_word_count[word] += 1
			else:
				query_word_count[word] = 1

		#query_raw_tf = {"word1": frequency of word1, ...}
		#words are those that the documents contain
		query_raw_tf = {}
		for word in self.index.totalIndex:
			if word in query_word_count:
				query_raw_tf[word] = query_word_count[word]
			else:
				query_raw_tf[word] = 0

		#calculate magnitude of the query
		query_mag = 0
		for word in query_word_count:
			query_mag += query_word_count[word]**2
		query_mag = pow(query_mag, 0.5)
		
		#calculate the tf of the query
		#query_tf = {"word1": tf1, ...}
		query_tf = {}
		for word in query_raw_tf.keys():
			query_tf[word] = query_raw_tf[word]/query_mag

		#calculate the tfidf of the query
		#query_tfidf = {"word1": tfidf1, ...}
		query_tfidf = {}
		for word in query_tf:
			query_tfidf[word] = query_tf[word] * self.index.idf[word]	

		return query_tfidf

	def cosine(self, vector1, vector2):
		if len(vector1) != len(vector2):
			print("Error at cosine similarity, two vectors are not same length")
			return -1

		mag = pow(sum(map(lambda x: x**2, vector1)) + sum(map(lambda x: x**2, vector2)), .5)
		sumproduct = 0
		for i in range(0, len(vector1)):
			sumproduct += vector1[i] * vector2[i]
		return sumproduct/mag

	def get_vector(self, tfidf):
		vector = []
		for word in tfidf:
			vector.append(tfidf[word])
		return vector

	def search_with_all_docs(self, query):
		query_tfidf = self.query_term_frequency_inversed_document_frequency(query)
		vector_query = self.get_vector(query_tfidf)
		results = {}
		for filename in self.index.tfidf:
			vector_doc = self.get_vector(self.index.tfidf[filename])
			results[filename] = self.cosine(vector_query, vector_doc)
		# sorted_results = sorted(results.items(), key=operator.itemgetter(1))
		# sorted_results.reverse()
		return results