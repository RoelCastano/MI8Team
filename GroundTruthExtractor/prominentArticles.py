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

# each of the clickstream files have different coloumns and therefore we can enumerate them below
PREV_COL = 0
CURR_COL = 1
TYPE_COL = 2
COUNT_COL = 3

# assign variables
currentArticle = ''
sessionSum = 0
numberOfTruth = 1000
truthHeap = []
lineCnt = 0

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

        # if the trail between articles is anything other than through a link then we ignore tuple
        if lineSplit[TYPE_COL] != 'link':
            continue

        # if the row represents a link from a non-existing article OR the main page then ignore tuple
        if not lineSplit[PREV_COL] or 'other-' in lineSplit[PREV_COL] or lineSplit[PREV_COL] == 'Main_Page':
            continue

        # if the article contains an @ we ignore. We use it as a separator later on
        if '@' in lineSplit[PREV_COL]:
            continue

        # if the row represents a link to a non-existing article OR the main page then ignore tuple
        if not lineSplit[CURR_COL] or 'other-' in lineSplit[CURR_COL] or lineSplit[CURR_COL] == 'Main_Page':
            continue
        
        # if the currentArticle "pointer" has not been set then set it to current article
        if not currentArticle: 
            currentArticle = lineSplit[PREV_COL]

        # aggregate over the number of outgoing trails from an article and store the articles that redirects most users to other pages.
        if currentArticle == lineSplit[PREV_COL]:
            sessionSum += int(lineSplit[COUNT_COL].replace("\n", ""))
        else:
            truthHeap.append([sessionSum, currentArticle])
            currentArticle = lineSplit[PREV_COL]
            sessionSum = int(lineSplit[COUNT_COL].replace("\n", ""))

# sort the articles after ID / name and combine/merge instances of the same articles to get an aggregated count
truthHeap = sorted(truthHeap, key=lambda truthHeap_entry: truthHeap_entry[1], reverse = False) 
for i, val in enumerate(truthHeap):
    if i < len(truthHeap)-1 and truthHeap[i][1] == truthHeap[i+1][1]:
        truthHeap[i+1][0] += truthHeap[i][0]
        truthHeap[i][0] = 0
    
# sort articles with respect to outgoing click count. Select n of the most prominent articles and forget the rest
truthHeap = sorted(truthHeap, key=lambda truthHeap_entry: truthHeap_entry[0], reverse = True) 
truthHeap = truthHeap[:numberOfTruth]

# order the remaining article after A-Z
truthHeap = sorted(truthHeap, key=lambda truthHeap_entry: truthHeap_entry[1], reverse = False) 

# save the most prominent articles to a file: line separated
seeds = open('prominentArticles.txt', 'w')
lineCnt = 0
for article in truthHeap:
    lineCnt += 1
    seeds.write(article[1])
    if numberOfTruth > lineCnt:
        seeds.write("\n")
seeds.close()

# if we have extracted data for less than 100 articles its safe to print to console        
if numberOfTruth < 100:
    pprint.pprint(truthHeap)

print("prominentArticles.txt has been generated")