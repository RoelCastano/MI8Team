from sklearn.metrics import jaccard_similarity_score
from math import*
import matplotlib.pyplot as plt
import numpy as np
import getopt
import os, sys
import re

Outgoing_Links = {}
Incoming_Links = {}
W=0
Histogram = []

def intersection_cardinality(x,y):
    return len(set.intersection(*[set(x), set(y)]))
    
def union_cardinality(x,y):
    return len(set.union(*[set(x), set(y)]))
    
def jaccard(x,y):
    return (intersection_cardinality(x,y)/float(union_cardinality(x,y)))*100
    
def dice(x,y):
    return 2*(intersection_cardinality(x,y)/float(len(x)+len(y)))*100
    
def normalized_google_distance(x,y,w):
    if intersection_cardinality(x,y) == 0 :
        return 
    if len(x) == 0 or len(y) == 0 :
        return 1
    num = log10(max(len(x),len(y)))-log10(intersection_cardinality(x,y))
    den = log10(w)-log10(min(len(x),len(y)))
    return num/float(den)        

def build_sets(filename):
    print("Reading ",filename," ... ")
    regex = r"^(?P<article>[^\s]*)\t(?P<target>[^\s]*)\s"
    with open(filename,'r', encoding="utf-8") as f:
        lines  = f.readlines()
        for line in lines:
            link = re.search(regex,line)
            if link is not None:
                article = link.group('article')
                target = link.group('target')
                add_link(article,target)                                   
    f.close()
    set_W()
    print("File read. Found %d articles." %(W))

def add_link(article,target):
    global Outgoing_Links
    global Incoming_Links
     
    # add articles to the dictionary
    # print("Adding ",article," --> ",target)
    if article not in Outgoing_Links.keys():
        Outgoing_Links[article] = []
    if target not in Incoming_Links.keys():
        Incoming_Links[target] = []

    # add the articles to the links sets
    if target not in Outgoing_Links[article] :
        Outgoing_Links[article].append(target)
    if article not in Incoming_Links[target] :
        Incoming_Links[target].append(article)
    
def print_feature(opt,output_file):
    global Histogram
    print("Creating new relatedness feature file ...")
    with open(output_file,"w",encoding="utf-8") as out:
        for title1 in Outgoing_Links:
            for title2 in Outgoing_Links[title1]:
                link_title = title1+"@"+title2
                relatedness = get_relatedness(opt,title1,title2)
                out.write(link_title+"\t%f" % (relatedness)+"\n")
                Histogram.append(relatedness)
    out.close()
    print("Done : ",output_file)

def print_histogram():
    global Histogram
    hist, bins = np.histogram(Histogram, bins=50)
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hist, align='center', width=width)
    plt.show()    

def set_W():
    global W
    W=union_cardinality(Outgoing_Links.keys(),Incoming_Links.keys())
 
def get_relatedness(opt,articleA,articleB):

    # set of links to and from article A
    if articleA in Outgoing_Links :
        outgoing_links_A = Outgoing_Links[articleA]
    else :
        outgoing_links_A =[]
    if articleA in Incoming_Links :
        incoming_links_A = Incoming_Links[articleA]
    else :
        incoming_links_A =[]
    
    set_A = outgoing_links_A + incoming_links_A
    
    # set of links to and from article B
    if articleB in Outgoing_Links :
        outgoing_links_B = Outgoing_Links[articleB]
    else :
        outgoing_links_B =[]
    if articleB in Incoming_Links :
        incoming_links_B = Incoming_Links[articleB]
    else :
        incoming_links_B =[]
    set_B = outgoing_links_B + incoming_links_B
    
    # Get the option metric
    if opt == 'j':
        return jaccard(set_A,set_B)
    if opt == 'd':
        return dice(set_A,set_B)
    if opt == 'g':
        return normalized_google_distance(set_A,set_B,W)
      
def main():
    try:
        opts,args=getopt.getopt(sys.argv[1:],"jdg",["Jaccard coefficient","Dice's measure","Normalized Google distance"])
    except getopt.GetoptError as err:
        #print help information and exit:
        print(err)
        usage()
        sys.exit(2)

    build_sets(args[0])
    # print(Incoming_Links)
    for o,a in opts:
        if o == "-j":
            print_feature('j','jaccard_feature.txt')
        elif o =="-d":
            print_feature('d','dice_feature.txt')
        elif o =="-g":
            print_feature('g','normalized_google_distance_feature.txt')
        else :
            assert False,"unhandled option"
            
    print_histogram()
            
if __name__ == "__main__":
    main()