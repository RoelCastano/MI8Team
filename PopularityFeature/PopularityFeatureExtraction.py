import numpy as np
import heapq
import pprint
import os
import base64


# check if we on Philips PC (by checking OS type)
testingOnPhilipsPC = os.name == 'nt'

# set file path to OrderedLinkFile file
GroundTruthFile = r'/data/xxx.txt'
if testingOnPhilipsPC:
    GroundTruthFile = r'C:\Users\phili_000\Source\Repos\MI8Team\processed data\groundTruth.txt'

####### set file path to prominent article file
######prominentArticlesFile = r'/data/prominentArticles_032016_1k.txt'
######if testingOnPhilipsPC:
######    prominentArticlesFile = r'C:\Users\phili_000\Source\Repos\MI8Team\processed data\prominentArticles_032016_1k.txt'

# set file path to clickstream file
clickstreamFile = r'/data/2013_03_clickstream.tsv'
if testingOnPhilipsPC:
    clickstreamFile = r'C:\Users\phili_000\Desktop\MI8 data\2016_03\2016_03_clickstream.tsv'

# assign variables
currentArticle = ''
lineCnt = 0

# each of the clickstream files have different coloumns and therefore we can enumerate them below
PREV_COL = 0
CURR_COL = 1
TYPE_COL = 2
COUNT_COL = 3

# for the GroundTruthFile
GT_RANK_COL = 0
GT_ID_COL = 1
GT_QID_COL = 2

links = {}

with open(GroundTruthFile) as f:
    for line in f:

        # if we are at the end
        if not line:
            break

        # parse line into array
        lineSplit = line.split('\t')

        # extract line information
        id_split = lineSplit[GT_ID_COL].split('@')
        prev = id_split[0]
        curr = lineSplit[GT_ID_COL][len(prev)+1:]

        links[base64.b64encode(curr)] = [0, 0]






with open(clickstreamFile) as f:
        for line in f:
        
            # increment line counter
            lineCnt += 1

            # parse line into array
            lineSplit = line.split('\t')

            # if the trail between articles is anything other than through presumed search or social
            if lineSplit[TYPE_COL] != 'other' and lineSplit[TYPE_COL] != 'external' or not lineSplit[CURR_COL]:
                continue

            curr_encoded = base64.b64encode(lineSplit[CURR_COL])

            # if the page being reffered to is not in our dataset then ignore
            if not curr_encoded in links:
                continue

        
            count = int(lineSplit[COUNT_COL].replace("\n", ""))     
            if lineSplit[TYPE_COL] == 'external' and (lineSplit[PREV_COL] == 'other-google' or lineSplit[PREV_COL] == 'other-bing' or lineSplit[PREV_COL] == 'other-yahoo' or lineSplit[PREV_COL] == 'other-search'):
                links[curr_encoded][0] = links[curr_encoded][0] + count
            elif lineSplit[TYPE_COL] == 'other' and lineSplit[PREV_COL] and lineSplit[PREV_COL] == "Main_Page":
                links[curr_encoded][0] = links[curr_encoded][0] + count  
            elif lineSplit[TYPE_COL] == 'external' and (lineSplit[PREV_COL] == 'other-facebook' or lineSplit[PREV_COL] == 'other-twitter'):
                links[curr_encoded][1] = links[curr_encoded][1] + count 
 



popularityFeatureForAnalysis = open('popularityFeatureForAnalysis.txt', 'w')

with open(GroundTruthFile) as f:
    for line in f:

        # if we are at the end
        if not line:
            break

        # increment line counter
        lineCnt += 1

        # parse line into array
        lineSplit = line.split('\t')

        # extract line information
        rank = lineSplit[GT_RANK_COL] 
        id_split = lineSplit[GT_ID_COL].split('@')
        prev = id_split[0]
        curr = lineSplit[GT_ID_COL][len(prev)+1:]
        qid_split = lineSplit[GT_QID_COL].replace("\n", "").split(':')
        qid = qid_split[1] 

        curr_encoded = base64.b64encode(curr)

    
        externalSearches = links[curr_encoded][0]
        socialMedias = links[curr_encoded][1]

        sumCountsExternal = externalSearches + socialMedias

        if sumCountsExternal > 0:
            externalSearchToSocialRatio = str(externalSearches / float(sumCountsExternal))
        else: 
            externalSearchToSocialRatio = 0



        #popularityFeaturesTmp.write(lineSplit[GT_ID_COL] + "\t" + prev + "\t" + curr + "\t" + str(qid) + "\t" + str(externalSearches) + "\t" + str(socialMedias) + "\n")
        popularityFeatureForAnalysis.write(str(rank) + "\t" + prev + "\t" + curr + "\t" + str(qid) + "\t" + str(externalSearches) + "\t" + str(socialMedias) + "\n")




popularityFeatureForAnalysis.write(str(1) + "\t" + str(1) + "\t" + str(1) + "\t" + str(1) + "\t" + str(1) + "\t" + str(1) + "\n")