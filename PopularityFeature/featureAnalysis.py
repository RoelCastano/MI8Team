import numpy as np
import heapq
import pprint
import os
import base64
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from random import randint
from scipy.optimize import curve_fit



plt.style.use('ggplot')


rank = []
externalSearches = []
socialMedias = []
internalSearches = []
internalToExternalSearchRatio = []
randomnum = []
titleSim = []

externalSearchesDistriF = []

qList = []
qIter = 1

articleSingleSearch = []

popArtDict = {}

posSearchInPDF = []

abovCnt = 0
belCnt = 0
thresholdEval = 191

with open('popularityFeatureForAnalysis.txt') as f:
    for line in f:

        # parse line into array
        lineSplit = line.split('\t')


        if int(lineSplit[3]) == qIter:
            qList.append(lineSplit)
        else:

            rankTmp = []
            externalSearchesTmp = []
            socialMediasTmp = []
            qRankDec = len(qList)
            
            for qLine in qList:

                prevSplit = qLine[1].split('_')
                currSplit = qLine[2].split('_')
                titleSim.append(len(set(prevSplit) & set(currSplit)) / float(len(set(prevSplit) | set(currSplit))))

                # extract line information
                rankTmp.append(float(qLine[0])) 
                #rankTmp.append(float(qRankDec)) 
                qRankDec = qRankDec-1

                externalSearchesTmp.append(float(qLine[4])) 
               #! socialMediasTmp.append(float(qLine[5])) 

                if not popArtDict.has_key(qLine[2]):
                    articleSingleSearch.append(float(qLine[4]))
                    popArtDict[qLine[2]] = True


               #! externalSearchToSocialRatio.append(float(qLine[6])) 
               #! randomnum.append(float(randint(0,9)))

            lenranktmp = len(rankTmp)
            if lenranktmp >= thresholdEval: 
                belCnt += thresholdEval
                abovCnt += lenranktmp - thresholdEval
            else: 
                belCnt += lenranktmp

            rankTmp = [(x)/max(rankTmp) for x in rankTmp]
            rank = rank + rankTmp
        
            #externalSearchesTmp = np.array(externalSearchesTmp)
            #externalSearchesTmp = np.ma.log(externalSearchesTmp / 362) / 242
            #externalSearchesTmp = externalSearchesTmp.tolist(externalSearchesTmp)

            #med = np.median(externalSearchesTmp)
            #cnt = np.size(externalSearchesTmp)
            #externalSearchesTmp = sorted(externalSearchesTmp)



            #externalSearchesTmp = np.ma.log(externalSearchesTmp)
            #externalSearchesTmp = np.ma.log(externalSearchesTmp)
            #externalSearchesTmp = np.ma.log(externalSearchesTmp)
            externalSearchesTmp = np.ma.log(externalSearchesTmp)
            externalSearchesTmp = externalSearchesTmp.tolist(externalSearchesTmp)
            externalSearchesTmp = [(x)/max(externalSearchesTmp) for x in externalSearchesTmp]
            externalSearches = externalSearches + externalSearchesTmp


            ####externalSearchesDistri = []
            ####distinct = list(set(externalSearchesTmp))
            ####for tmp in externalSearchesTmp:
            ####    externalSearchesDistri.append( sum(float(i < tmp) for i in distinct) )                
            ####externalSearchesDistri = [(x)/max(externalSearchesDistri) for x in externalSearchesDistri]
            ####externalSearchesDistriF = externalSearchesDistriF + externalSearchesDistri


           #! socialMediasTmp = np.ma.log(socialMediasTmp)
           #! socialMediasTmp = socialMediasTmp.tolist(socialMediasTmp)
           #! socialMediasTmp = [(x)/sum(socialMediasTmp) for x in socialMediasTmp]
           #! socialMedias = socialMedias + socialMediasTmp
                      

            qList = [lineSplit]
            qIter = int(lineSplit[3])

        


#articleSingleSearch = np.ma.log(articleSingleSearch)
#articleSingleSearch = articleSingleSearch.tolist(articleSingleSearch)


rank = np.array(rank)
externalSearches = np.array(externalSearches)
socialMedias = np.array(socialMedias)
internalSearches = np.array(internalSearches)
internalToExternalSearchRatio = np.array(internalToExternalSearchRatio)
posSearchInPDF = np.array(posSearchInPDF)
externalSearchesDistriF = np.array(externalSearchesDistriF)

corr_rank = np.corrcoef(rank, rank)
corr_externalSearches = np.corrcoef(rank, externalSearches)
####corr_externalSearchesD = np.corrcoef(rank, externalSearchesDistriF)
#corr_externalSearches = np.corrcoef(rank, posSearchInPDF)


#!corr_socialMedias = np.corrcoef(rank, socialMedias)
#!corr_externalSearchToSocialRatio = np.corrcoef(rank, externalSearchToSocialRatio)
corr_titleSim = np.corrcoef(rank, titleSim)

# http://www.biddle.com/documents/bcg_comp_chapter2.pdf
# page 14 - The Coefficient of Determination 

#externalSearches = np.log( externalSearches )

#!sigma = np.std(socialMedias)
#!mu = np.mean(socialMedias)
#!med = np.median(socialMedias)










# demonstration of linear log-log
y,binEdges=np.histogram(articleSingleSearch,bins=500, range = None, normed=True)
bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
plt.plot(bincenters,y,'-')
#plt.axis([exp(, 1, 0, 0.000012])
#plt.xticks(articleSingleSearch)
plt.gca().set_xscale("log")
plt.gca().set_yscale("log")
plt.xlabel(r'$ search(\beta) $', fontsize=20)
plt.ylabel('Probability Density', fontsize=20)
#plt.title(r'$\mathrm{PDF: Histogram of article search interest}\ $')
plt.show()


y,binEdges=np.histogram(externalSearches,bins=200, range = None, normed=True)
bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
plt.plot(bincenters,y,'-')
#plt.gca().set_xscale("log")
#plt.gca().set_yscale("log")
plt.show()

haha = np.max(bincenters)




sigma = np.std(y)
mu = np.mean(y)
med = np.median(y)
sum = np.sum(y)


#### SHOW HOW FEATURES CAN FIT AN EXPONENTIAL LINE

# the histogram of the data
n, bins, patches = plt.hist(articleSingleSearch, 500)

plt.xlabel('Articles')
plt.ylabel('Probability')
plt.title(r'$\mathrm{Searches:}\ \mu=100,\ \sigma=15$')
#plt.axis([0, 1, 0, 0.000012])
plt.grid(True)
plt.gca().set_xscale("log")
plt.gca().set_yscale("log")
plt.show()





n, bins, patches = plt.hist(socialMedias, 500)

plt.xlabel('Articles')
plt.ylabel('Probability')
plt.title(r'$\mathrm{Social media:}\ \mu=100,\ \sigma=15$')
#plt.axis([0, 1, 0, 0.000012])
plt.grid(True)
#plt.gca().set_xscale("log")
plt.gca().set_yscale("log")
plt.show()



hyyy = 0