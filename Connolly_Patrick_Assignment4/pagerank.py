#Python 3.0
import re
import os
import collections
import time
#import other modules as needed

class pagerank:
	
	def pagerank(self, input_file):
	#function to implement pagerank algorithm
	#input_file - input file that follows the format provided in the assignment description
		alpha=.15
		
		file=open(input_file)
		
		page_count=int(file.readline())
		edge_count=int(file.readline())
		
		
	def read_input(input_file):
		