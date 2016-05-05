import numpy as np
import heapq
import pprint
import os

# load list of prominent article into memory
prominentArticles = []
with open('prominentArticles.txt') as f:
    for line in f:
        prominentArticles.append(line.replace("\n", ""))

# sort prominent articles A-Z
prominentArticles = sorted(prominentArticles) 

# create file for results
groundTruthList = open('groundTruth.txt', 'w')

# set line counter
lineCnt = 0

for promArticle in prominentArticles:
        
    # increment line counter
    lineCnt += 1


    # save all related curr articles in lists from both pair-file and orderedClickList
    # use the fact that they are both ordered alphabetically

    
    groundTruthList.write("# article A \n")
    groundTruthList.write("2123 qid:12 # articleB \n")
    break