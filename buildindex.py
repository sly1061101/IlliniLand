#input = [file1, file2, ...]
#res = {filename: [world1, word2]}

import re
import math

class BuildIndex:

	def __init__(self, filename):
		self.filename = filename
		self.file_to_terms = self.process_files()
		self.num_of_docs = len(self.file_to_terms)
		self.regdex = self.make_indices(self.file_to_terms)
		self.totalIndex = self.fullIndex()
		self.tf = self.term_frequency()
		self.df = self.document_frequency()
		self.idf = self.inversed_document_frequency()
		self.tfidf = self.term_frequency_inversed_document_frequency()

	#input: list of filename
	#output: {file1:["word1", "word2", ...], ...}
	def process_files(self):
		file_to_terms = {}
		with open(self.filename) as fp:  
			for cnt, line in enumerate(fp):
			#stopwords = open('stopwords.txt').read().close()
				pattern = re.compile('[\W_]+')
				file_to_terms[cnt] = line.lower();
				file_to_terms[cnt] = pattern.sub(' ',file_to_terms[cnt])
				re.sub(r'[\W_]+','', file_to_terms[cnt])
				file_to_terms[cnt] = file_to_terms[cnt].split()
				#file_to_terms[file] = [w for w in file_to_terms[file] if w not in stopwords]
				#file_to_terms[file] = [stemmer.stem_word(w) for w in file_to_terms[file]]
		return file_to_terms

	def avg_file_len(self):
		sum = 0
		for i in range(0, self.num_of_docs):
			sum += len(self.file_to_terms[i])
		return sum/self.num_of_docs

	#input = [word1, word2, ...]
	#output = {word1: [pos1, pos2], word2: [pos2, pos434], ...}
	def index_one_file(self, termlist):
		fileIndex = {}
		for index, word in enumerate(termlist):
			if word in fileIndex.keys():
				fileIndex[word].append(index)
			else:
				fileIndex[word] = [index]
		return fileIndex

	#input = {filename: [word1, word2, ...], ...}
	#res = {filename: {word: [pos1, pos2, ...]}, ...}
	def make_indices(self, termlists):
		total = {}
		for filename in termlists.keys():
			total[filename] = self.index_one_file(termlists[filename])
		return total

	#input = {filename: {word: [pos1, pos2, ...], ... }}
	#res = {word: {filename: [pos1, pos2], ...}, ...}
	def fullIndex(self):
		total_index = {}
		indie_indices = self.regdex
		for filename in indie_indices.keys():
			for word in indie_indices[filename].keys():
				if word in total_index.keys():
					if filename in total_index[word].keys():
						total_index[word][filename].append(indie_indices[filename][word][:])
					else:
						total_index[word][filename] = indie_indices[filename][word]
				else:
					total_index[word] = {filename: indie_indices[filename][word]}
		return total_index

	def raw_term_frequenct(self):
		raw_tf = {}
		for filename in range(0, self.num_of_docs):
			raw_tf[filename] = {}
			for word in self.totalIndex.keys():
				if filename in self.totalIndex[word]:
					raw_tf[filename][word] = len(self.totalIndex[word][filename]) 
				else:
					raw_tf[filename][word] = 0
		return raw_tf		

	#tf = {filename 1, {word1:tf1, word2:tf2, ...}, ...}
	def term_frequency(self):
		#raw_tf simply counts frequencies of words in each document
		tf = {}
		raw_tf = self.raw_term_frequenct();
		mags = self.magnitudes(raw_tf)
		for filename in range(0, self.num_of_docs):
			tf[filename] = {}
			for word in self.totalIndex.keys():
				tf[filename][word] = raw_tf[filename][word] / mags[filename]
		return tf

	#input: raw_tf = {filename 1, {word1:tf1, word2:tf2, ...}, ...}
	#output: mags = {filename 1: mag1, ...}
	def magnitudes(self, raw_tf):
		mags = {}
		for filename in raw_tf.keys():
			vector = []
			for word in raw_tf[filename]:
				vector.append(raw_tf[filename][word])
			mags[filename] = pow(sum(map(lambda x: x**2, vector)),.5)
		return mags

	#df = {word1:number of documents contains word1, word2:number of documents contains word2, ...}
	def document_frequency(self):
		df = {}
		for word in self.totalIndex:
			df[word] = len(self.totalIndex[word])
		return df

	#idf = {word1:idf1, word2:idf2, ...}
	def inversed_document_frequency(self):
		idf = {}
		for word in self.df:
			idf[word] = math.log(1 + self.num_of_docs/self.df[word])
		return idf

	def term_frequency_inversed_document_frequency(self):
		tfidf = {}
		for filename in range(0, self.num_of_docs):
			tfidf[filename] = {}
			for word in self.tf[filename].keys():
				tfidf[filename][word] = self.tf[filename][word] * self.idf[word]	
		return tfidf
