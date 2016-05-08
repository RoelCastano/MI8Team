from sklearn.metrics import jaccard_similarity_score
from math import*
import getopt
import os, sys
    
def intersection_cardinality(x,y):
    return len(set.intersection(*[set(x), set(y)]))
    
def union_cardinality(x,y):
    return len(set.union(*[set(x), set(y)]))
    
def jaccard(x,y):
    return intersection_cardinality(x,y)/float(union_cardinality(x,y))
    
def dice(x,y):
    return intersection_cardinality(x,y)/float(len(x)+len(y))
    
def normalized_google_distance(x,y,w):
    num = log(max(len(x),len(y))-log(intersection_cardinality(x,y)))
    den = log(len(w))-log(min(len(x),len(y)))
    return num/float(den)
    
def main():
    try:
    	opts,args=getopt.getopt(sys.argv[1:],"jdg:",["Jaccard coefficient","Dice's measure","Normalized Google distance"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        usage()
        sys.exit(2)
    for o,a in opts:
        if o == "-j":
            print("Jaccard:",jaccard(args[0],args[1]))
        elif o =="-d":
            print("Dice:",dice(args[0],args[1]))
        elif o =="-g":
            print("Normalized Google distance : ",normalized_google_distance(args[0],args[1],a))
        else :
            assert False,"unhandled option"
			
if __name__ == "__main__":
    main()