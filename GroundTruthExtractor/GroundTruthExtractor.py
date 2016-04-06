import numpy as np
import heapq
import pprint
import os

# check if we on Philips PC (by checking OS type)
testingOnPhilipsPC = os.name == 'nt'

# set file path to clickstream file
clickstreamFile = r'/data/2013_03_clickstream.tsv'
if testingOnPhilipsPC:
    clickstreamFile = r'C:\Users\phili_000\Desktop\MI8 data\2016_03\2016_03_clickstream.tsv'

# assign variables
currentArticle = ''
sessionSum = 0
numberOfTruth = 10
truthHeap = []
lineCnt = 0

# each of the clickstream files have different coloumns and therefore we can enumerate them below
PREV_COL = 0
CURR_COL = 1
TYPE_COL = 2
COUNT_COL = 3

# loop through clickstream file to extract the most "important" articles
with open(clickstreamFile) as f:
    for line in f:
        
        # increment line counter
        lineCnt += 1

        # skip the first line. It contains no useful data
        if lineCnt == 1:
            continue

        # parse line into array
        lineSplit = line.split('\t')

        # if the currentArticle "pointer" has not been set then set it to current article
        if not currentArticle: 
            currentArticle = lineSplit[CURR_COL]

        # if the row represents a link to a non-existing article then ignore tuple
        if not lineSplit[CURR_COL]:
            continue
        
        # aggregate over the number of outgoing trails from an article and store the articles that redirects most users to other pages.
        # articles are remembered using a homebaked max-heap storing the most interesting "numberOfTruth"-articles
        if currentArticle == lineSplit[CURR_COL]:
            sessionSum += int(lineSplit[COUNT_COL])
        else:
            if len(truthHeap) < numberOfTruth or truthHeap[-1][0] < sessionSum:
                truthHeap.append([sessionSum, lineSplit[CURR_COL]])
                if len(truthHeap) > numberOfTruth:
                    truthHeap = sorted(truthHeap, key=lambda truthHeap_entry: truthHeap_entry[0], reverse = True) 
                    truthHeap.pop();
                    break # TODO: remove line
            currentArticle = lineSplit[CURR_COL]
            sessionSum = int(lineSplit[COUNT_COL])

# if we have extracted data for less than 100 articles its safe to print to console        
if numberOfTruth < 100:
    pprint.pprint(truthHeap)

# TODO: create or empty file for ground truth
groundTruthFile = open('groundtruth.txt', 'w+')

# reset line counter
lineCnt = 0

# loop through clickstream file to ...
with open(clickstreamFile) as f:
    for line in f:
        
        # increment line counter
        lineCnt += 1

        # skip the first line. It contains no useful data
        if lineCnt == 1:
            continue

        # parse line into array
        lineSplit = line.split('\t')
        
        # if the prev article is in the set of important articles then:
            # add the curr:number to ground truth file at its respective line
        if lineSplit[PREV_COL]:
            match = [item for item in truthHeap if item[1] == lineSplit[CURR_COL]]
            if match:
                index = truthHeap.index(match[0])
                fooo = 1
                # TODO: store the tuple somehow
                

# TODO: save results to file in correct formatting