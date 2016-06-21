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
prominentArticles = sorted(prominentArticles, key=str.lower) 

# create file for results
groundTruthList = open('groundTruth.txt', 'w')

# set line counter
lineCnt = 0

ocl = open("orderedClickList.txt", "r")
ocl.readline() # skip first row
line = ocl.readline() # read first line
line = line.split('\t')
clicks = int(line[0])
prevLine = line[1].replace("\n", "")
currLine = line[2].replace("\n", "")

ap = open("articlePairs.txt", "r")
apline = ap.readline() # read first line
apline = apline.split('\t')
apprevLine = apline[0].replace("\n", "")
apcurrLine = apline[1].replace("\n", "")

for promArticle in prominentArticles:
        
    # increment line counter
    lineCnt += 1

     # save all related curr articles in lists from both pair-file and orderedClickList
    # use the fact that they are both ordered alphabetically
    
    linkedArticleList = []

    while prevLine == promArticle:
        linkedArticleList.append([currLine, clicks])
        line = ocl.readline()
        if not line:
            prevLine = "NO_MORE_PROMINENT"
            break
        line = line.split('\t')
        clicks = int(line[0])
        prevLine = line[1].replace("\n", "")
        currLine = line[2].replace("\n", "")

    linkedArticleSet = {}
    for lal in linkedArticleList:
        linkedArticleSet[lal[0].lower()] = True

    while apprevLine.lower() < prevLine.lower() or prevLine == "NO_MORE_PROMINENT":
        if apprevLine == promArticle and not linkedArticleSet.has_key(apcurrLine.lower()):
            linkedArticleList.append([apcurrLine, 0])
        line = ap.readline()
        if not line:
            break
        line = line.split('\t')
        apprevLine = line[0].replace("\n", "")
        apcurrLine = line[1].replace("\n", "")


    # print the prom article comment
    #groundTruthList.write("# " + promArticle + "\n")

        
    mm = 1

    # loop through the 2 lists (ordered clicks first) and print lines
    # if an instance exist in both lists do not print the 2. time
    #for oclArticle in linkedArticleList:
    #    groundTruthList.write(str(oclArticle[1]) + " qid:" + str(lineCnt) + " # " + oclArticle[0] + "\n")

    for oclArticle in linkedArticleList:
        groundTruthList.write(str(oclArticle[1]) + "\t" + promArticle + "@" + str(oclArticle[0]) + "\t" + " qid:" + str(lineCnt) + "\n")

    
print("groundTruth.txt has been generated")