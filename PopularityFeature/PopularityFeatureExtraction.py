import numpy as np
import heapq
import pprint
import os

# check if we on Philips PC (by checking OS type)
testingOnPhilipsPC = os.name == 'nt'

# set file path to OrderedLinkFile file
OrderedLinkFile = r'/data/orderedClickList_032016_1k.txt'
if testingOnPhilipsPC:
    OrderedLinkFile = r'C:\Users\phili_000\Source\Repos\MI8Team\processed data\orderedClickList_032016_1k.txt'

# set file path to prominent article file
prominentArticlesFile = r'/data/prominentArticles_032016_1k.txt'
if testingOnPhilipsPC:
    prominentArticlesFile = r'C:\Users\phili_000\Source\Repos\MI8Team\processed data\prominentArticles_032016_1k.txt'

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

# for the OrderedLinkFile
PA_RANK_COL = 0
PA_PREV_COL = 1
PA_CURR_COL = 2
PA_COUNT_COL = 3

# TODO: load prominent articles into memory

# TODO: loop through all clickstream tuples and accumulate popularity values for articles within prominent set

# TODO: loop through ordered clicklist file and create feature file 
