#Python 3.0
import re
import os
import collections
import time
import math
import random
#import other modules as needed

class index:
	def __init__(self, doc_path, stoplist_path):
		self.doc_path = doc_path
		self.stoplist_path = stoplist_path        
        
		self.stopwords = {}
		self.token_set = {}
        
		self.doc_id = {}
		self.docs ={}

		self.collection = collections.defaultdict(list)
		
		self.document_mag = {}
		self.document_vect = {}
		
		self.champion_list = {}
		self.leaders = collections.defaultdict(list)
        
        
	def buildIndex(self):
		#function to read documents from collection, tokenize and build the index with tokens
		# implement additional functionality to support methods 1 - 4
		#use unique document integer IDs
		start=time.time()
		
		#generate doc ids
		docs = os.listdir(self.doc_path)
		for i, doc_name in enumerate(docs):
			self.doc_id[i] = doc_name
			
		#retrive stoplist
		stoplist = open(self.stoplist_path,"r").read()
		self.stopwords = re.sub('[^A-Za-z\n ]+', '', stoplist).split() 
		
		init_dict = collections.defaultdict(dict)
		
		for key, value in self.doc_id.items():
			#read in the collection
			document = open(self.doc_path + "/" + value , "r")
			
			#clean up docs
			file_text = document.read().lower()
			words = re.sub('[^A-Za-z\n]+' , '', file_text).split()
			words = [x for x in words if x not in self.stopwords]
			
			self.docs[key] = words
			for i, word in enumerate(words):
				if key in list(init_dict[word]):
					init_dict[word][key].append(i)
				else:
					init_dict[word][key] = [i]
					
		#get idf for all words
		for i in init_dict.keys():
			idf = math.log(len(self.doc_id) / len(init_dict[i].keys()), 10)
			self.collection[i].append(idf)
			for j in init_dict[i].keys():
				tf_idf = (1 + math.log(len(init_dict[i][j]), 10)) * idf
				self.collection[i].append((j, tf_idf, init_dict[i][j]))
        
		end=time.time()
		print("Time to build tf-idf index: ",'{:.20f}'.format(end-start), " seconds")
		
		
		#generate document vectors
		start = time.time()
		
		for doc in self.doc_id:
			document_vect = {}
			for k, v in self.collection.items():
				for i, v2 in enumerate(v):
					if i>0 & doc == v2[0]:
						document_vect[k]= v2[1]
			self.document_vect[doc]= document_vect
			
		end = time.time()
		print("Time to calculate document vectors: ", '{:.20f}'.format(end-start), " seconds")			
		
		
		#generate documeent magnitudes
		start = time.time()
		
		for i, value in self.docs.items():
			doc_mag = 0
			for k, v in self.collection.items():
				for j in range(1, len(v)):
					if v[j][0] == i:
						doc_mag += v[j][1] ** 2
			self.document_mag[i] = math.sqrt(doc_mag)
		
		end = time.time()
		print("Time to calculate document magnitudes: ", '{:.20f}'.format(end-start), " seconds")
		
		#generate champions list
		start = time.time()
		
		r= int(math.sqrt(len(self.doc_id)))+10
		for k, v in self.collection.items():
			sorted_list = v[1:]
			sorted_list.sort(key=lambda x: x[1], reverse=True)
			self.champion_list[k] = [x[0] for x in sorted_list[:r]]
			
		end = time.time()
		
		print("Time to build champion list: ", '{:.20f}'.format(end-start), " seconds")
		
		#generate leaders
		start = time.time()
		
		leader_index_size = math.floor(math.sqrt(len(self.doc_id)))
		leaders = set()
		while len(leaders) != leader_index_size:
			leaders.add(random.randint(1, len(self.doc_id)))
		
		for k in leaders:
			for doc in self.doc_id.keys():
				#get cosine similarity
				if self.cosine_similarity_docs(k,doc) > 0.05:
					self.leaders[k].append(doc)
					
		end = time.time()
		
		print("Time to build cluster pruning index: ", end-start , "seconds")
		
	def clean_query(self, query):
		query = query.split(" ")
		query = [x for x in query if x not in self.stopwords]
		return self.query_tf_idf(query)
		
	def exact_query(self, query_terms, k):
		#function for exact top K retrieval (method 1)
		#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
		start =time.time()
		q_tf_idf = self.clean_query(query_terms)

		scores = []
		for doc in self.doc_id.keys():
			scores.append((doc, self.cosine_similarity(q_tf_idf, doc)))
		scores.sort(key=lambda x: x[1], reverse=True)
		end = time.time()
		self.print_results(start, end, k, query_terms, scores, "exact retrieval")

	def inexact_query_champion(self, query_terms, k):
		#function for exact top K retrieval using champion list (method 2)
		#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
		start=time.time()
		q_tf_idf= self.clean_query(query_terms)
		
		scores = []
		for doc in self.leaders.keys():
			scores.append((doc, self.cosine_similarity(q_tf_idf, doc)))
		scores.sort(key=lambda x: x[1], reverse=True)

		final_list = []
		for x in range(len(scores)):
			for doc in self.leaders[scores[x][0]]:
				final_list.append((doc, scores[x][1]))
		end = time.time()
		self.print_results(start, end, k, query_terms, final_list, "cluster pruning")
		
		
	def inexact_query_index_elimination(self, query_terms, k):
		#function for exact top K retrieval using index elimination (method 3)
		#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
		# create list of docs that contain at least half the query terms
		start = time.time()
		q_tf_idf = self.clean_query(query_terms)

		# check how many terms of query the document has
		term_count = {}
		for t in q_tf_idf.keys():
			if t in self.collection.keys():
				v = self.collection[t]
				for i in range(1, len(v)):
					if v[i][0] in term_count.keys():
						term_count[v[i][0]] += 1
					else:
						term_count[v[i][0]] = 1

		# filter to documents with at least half
		final_list = []
		for k, v in term_count.items():
			if v >= len(q_tf_idf.keys()) / 2:
				final_list.append(k)

		scores = []
		for doc in final_list:
			scores.append((doc, self.cosine_similarity(q_tf_idf, doc)))
		scores.sort(key=lambda x: x[1], reverse=True)
		end = time.time()
		self.print_results(start, end, k, query_terms, scores, "index elimination")

	def inexact_query_cluster_pruning(self, query_terms, k):
		#function for exact top K retrieval using cluster pruning (method 4)
		#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
		start = time.time()
		q_tf_idf = self.clean_query(query_terms)

		scores = []
		for doc in self.leaders.keys():
			scores.append((doc, self.cosine_similarity(q_tf_idf, doc)))
		scores.sort(key=lambda x: x[1], reverse=True)

		final_list = []
		for x in range(len(scores)):
			for doc in self.leaders[scores[x][0]]:
				final_list.append((doc, scores[x][1]))
		end = time.time()
		self.print_results(start, end, k, query_terms, final_list, "cluster pruning")
		
		
	def cosine_similarity(self, q_tf_idf, doc):
		# get product of query and documents
		score = 0
		for k in q_tf_idf.keys():
			if k in self.collection.keys():
				v = self.collection[k]
				for i in range(1, len(v)):
					if v[i][0] == doc:
						score += v[i][1]

		q_mag = 0
		for k, v in q_tf_idf.items():
			for i in range(1, len(v)):
				q_mag += v[i][1] ** 2

		length = self.document_mag[doc] * math.sqrt(q_mag)

		if length != 0:
			cosine_score = score / length
		else:
			cosine_score = 0

		return cosine_score

	def cosine_similarity_docs(self, doc_1, doc_2):
		scores = 0

		doc_v1 = self.document_vect[doc_1]
		doc_v2 = self.document_vect[doc_2]

		for k, v in doc_v1.items():
			if k in doc_v2.keys():
				scores += v * doc_v2[k]

		length = math.sqrt(self.document_mag[doc_1] * self.document_mag[doc_2])
		if length > 0:
			cosine_score = scores / length
		else:
			cosine_score = 0

		return cosine_score
		
	
	@staticmethod
	def query_tf_idf(query):
		init_dict = collections.defaultdict(dict)
		final_dict = collections.defaultdict(list)

		for key, value in enumerate(query):
			word = query[key]
			if key in init_dict[value].keys():
				init_dict[word][0].append(key)
			else:
				init_dict[word][0] = [key]

		for i in init_dict.keys():
			idf = math.log(len(query) / len(init_dict[i].keys()), 10)
			final_dict[i].append(idf)
			for j in init_dict[i].keys():
				tf_idf = (1 + math.log(len(init_dict[i][j]), 10)) * idf
				final_dict[i].append((j, tf_idf, init_dict[i][j]))

		return final_dict
	
	
	def print_dict(self):
		#function to print the terms and posting list in the index
		for key, value in self.collection.items():
			print(key + ": [", end="")
			dict_item_count = len(value)
			dict_position = 1
			for doc_id, positions in value.items():
				print("(" + str(doc_id) + ", " + "".join(str(positions)) + ")", end="")
				if dict_position != dict_item_count:
					print(", ", end="")
				dict_position += 1
			print("]")

	def print_doc_list(self):
		# function to print the documents and their document id
		for key, value in self.doc_id.items():
			print("Doc ID:", key, "==>", value)
			
	def print_results(self, start, end, k, query, scores, method):
		print("Top", k, "result(s) for the query '", query, "' using", method, "method are:")
		for i in range(k):
			print((i + 1), ".", self.doc_id[scores[i][0]], "with score", scores[i][1])
		print("Results found in", '{:.20f}'.format(end - start), "seconds")


#main

obj = index("./collection" , "stop-list.txt")



print('n>>> Build Index')

queries = [
		"with without yemen yemeni",
		"german invasion of poland",
		"allied forces axis powers",
		"america enter the war",
		"is germany going to win"
		]

obj.buildIndex()

for query in queries:
	obj.exact_query(query, 10)
	obj.inexact_query_champion(query, 10)
	obj.inexact_query_index_elimination(query, 10)
	obj.inexact_query_cluster_pruning(query, 10)