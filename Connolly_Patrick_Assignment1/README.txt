Assignment 1 - Boolean Retrieval

Patrick Connolly
pconnol1@hawk.iit.edu
A20348060

Merge Algorithm
In my development of the merge algorithm, I closely followed the intersecting of common points such as the book describes. The mergelist function is what is called when the AND query is used for searching with multiple inputs. 
It will go through both postings in order of there appearance in the list and append them to a new list when they both are in the same posting. It will increase the pointer of one list if it is lower than the other to make both lists line up and returns the merged list at the end of the search.


85	@staticmethod
86   #function to combine result lists for query
87	def mergeList(list1, list2):
88		list1 = sorted(list1)
89		list2 = sorted(list2)
90		i, j = 0, 0
91		merged = []
92		while i < len(list1) and j < len(list2):
93			if list1[i] == list2[j]:
94				merged.append(list1[i])
95				i += 1
96				j += 1
97			elif list1[i] > list2[j]:
98				j += 1
99			else:
100				i += 1
101		return merged


To make a new query, at the end of the file add an obj.and_query(<array>) where the array is the terms you would like to search through in the collections folder.