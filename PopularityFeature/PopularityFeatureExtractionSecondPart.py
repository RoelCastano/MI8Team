import numpy as np
import heapq
import pprint
import os
import base64


# check if we on Philips PC (by checking OS type)
testingOnPhilipsPC = os.name == 'nt'

popularityFeatures = open('popularityFeatures_v3.txt', 'w')

qList = []
qIter = 1
with open('popularityFeatureForAnalysis.txt') as f:
    for line in f:

        # parse line into array
        lineSplit = line.split('\t')


        if int(lineSplit[3]) == qIter:
            qList.append(lineSplit)
        else:

            externalSearchesTmp = []
            socialMediasTmp = []
            titleSim = []

            for qLine in qList:

                # compute title similarity etc.
                prevSplit = qLine[1].split('_')
                currSplit = qLine[2].split('_')
                titleSim.append(len(set(prevSplit) & set(currSplit)) / float(len(set(prevSplit) | set(currSplit))))
                externalSearchesTmp.append(float(qLine[4])) 
                socialMediasTmp.append(float(qLine[5])) 

            externalSearchesDistri = []
            distinct = list(set(externalSearchesTmp))
            for tmp in externalSearchesTmp:
                externalSearchesDistri.append( sum(float(i < tmp) for i in distinct) )                
            externalSearchesDistri = [(x)/max(externalSearchesDistri) for x in externalSearchesDistri]
            
            externalSearchesTmp = np.ma.log(externalSearchesTmp)
            externalSearchesTmp = externalSearchesTmp.tolist(externalSearchesTmp)
            externalSearchesTmp = [(x)/max(externalSearchesTmp) for x in externalSearchesTmp]


            socialDistri = []
            distinct = list(set(socialMediasTmp))
            for tmp in socialMediasTmp:
                socialDistri.append( sum(float(i < tmp) for i in distinct) )                
            socialDistri = [(x)/max(socialDistri) for x in socialDistri]

            socialMediasTmp = np.ma.log(socialMediasTmp)
            socialMediasTmp = socialMediasTmp.tolist(socialMediasTmp)
            socialMediasTmp = [(x)/max(socialMediasTmp) for x in socialMediasTmp]

            tmpIter = 0
            for tmp in externalSearchesTmp:
                popularityFeatures.write(qList[tmpIter][1] + "@" + qList[tmpIter][2] + "\t" + str(titleSim[tmpIter]) + "\t" + str(externalSearchesTmp[tmpIter]) + "\t" + str(socialMediasTmp[tmpIter]) + "\t" + str(socialDistri[tmpIter]) + "\t" + str(externalSearchesDistri[tmpIter]) + "\n")
                tmpIter = tmpIter + 1

            qList = [lineSplit]
            qIter = int(lineSplit[3])

            wat = 1
            # TODO create lines with titleSim externalSearchesTmp socialMediasTmp socialDistri externalSearchesDistri and from qLine: instance ID