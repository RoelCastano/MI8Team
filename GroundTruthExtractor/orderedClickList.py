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

# load list of prominent article into memory
prominentArticles = []
with open('prominentArticles.txt') as f:
    for line in f:
        prominentArticles.append(line.replace("\n", ""))

# sort prominent articles A-Z
prominentArticles = sorted(prominentArticles) 

# set line counter
lineCnt = 0

# instantiate reversed list
inverseList = [[]] * len(prominentArticles)

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
        
        # if the trail between articles is anything other than through a link then we ignore tuple
        if lineSplit[TYPE_COL] != 'link':
            continue

        # if the row represents a link from a non-existing article OR the main page then ignore tuple
        if not lineSplit[PREV_COL] or 'other-' in lineSplit[PREV_COL] or lineSplit[PREV_COL] == 'Main_Page':
            continue

        # if the row represents a link to a non-existing article OR the main page then ignore tuple
        if not lineSplit[CURR_COL] or 'other-' in lineSplit[CURR_COL] or lineSplit[CURR_COL] == 'Main_Page':
            continue

        # if the prev article is in the set of important articles then:
            # add the curr:number to ground truth file at its respective line
        if lineSplit[PREV_COL]:
            match = lineSplit[PREV_COL] in prominentArticles
            if match:
                index = prominentArticles.index(lineSplit[PREV_COL])
                if not inverseList[index]:
                    inverseList[index] = inverseList[index][:]
                count = int(lineSplit[COUNT_COL].replace("\n", ""))
                inverseList[index].append([lineSplit[CURR_COL], count])

# sort all links by popularity for each article   
for i, article in enumerate(inverseList):
    article = sorted(article, key=lambda article_entry: article_entry[1], reverse = True) 
    inverseList[i] = article

# save file with 1 article pair pr line
orderedClickList = open('orderedClickList.txt', 'w')
orderedClickList.write("rank \tprev \tcurr\n")
articleSeedCnt = 0
for article in inverseList:
    rankNo = 0
    for articleLink in article:
        rankNo += 1
        orderedClickList.write(str(articleLink[1]) + "\t" + prominentArticles[articleSeedCnt] + "\t" + articleLink[0] + "\n")
    articleSeedCnt += 1
orderedClickList.close()

print("orderedClickList.txt has been generated")