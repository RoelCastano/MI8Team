"""This script computes the relatedness feature for all links in "all_from_prominent" file. 
It's using "prominent_intersection_all" file, which contains all the links from and to prominents 
to create for each of them the corresponding set of links.
The results (links sets and feature file) are stored in a new directory "relatedness_results".
"""

from math import*
import numpy as np
import getopt
import os, sys
import re



Links = {}
Non_Prominents = []
Non_Prominents_nb = 0
W=0

def intersection_cardinality(x,y):
    """Return the cardinality of the intersection of two sets
    Args:
	    x: first set
		y : second set
    """
    return len(set.intersection(*[set(x), set(y)]))
    
def union_cardinality(x,y):
    """Return the cardinality of the union of two sets
    Args:
	    x: first set
		y : second set
    """
    return len(set.union(*[set(x), set(y)]))
    
def jaccard(x,y):
    """Return the Jaccard coefficient of two vectors
    Args:
	    x: first set
		y : second set
    """
    return (intersection_cardinality(x,y)/float(union_cardinality(x,y)))
    
def dice(x,y):
    """Return the Dice's measure of two vectors
    Args:
	    x: first set
		y : second set
    """
    return 2*(intersection_cardinality(x,y)/float(len(x)+len(y)))
    
def normalized_google_distance(x,y,w):
    """Return the Jaccard coefficient of two vectors

    Args:
	    x : first set
		y : second set
		w : total number of articles in the entire data set
    """
    if intersection_cardinality(x,y) == 0 :
        return 1000
    elif len(x) == 0 or len(y) == 0 :
        return 1
    else :
        num = log10(max(len(x),len(y)))-log10(intersection_cardinality(x,y))
        den = log10(w)-log10(min(len(x),len(y)))   
        return num/float(den)

def build_sets(set_file, links_file,prominent_links_file):
    """Build the links sets for each prominent
    Args:
	    set_file : output file where to store sets
		links file : file listing all links (both outgoing and incoming) from prominents
		prominent_links_file : file listing the links from prominents
    """
    # if the links file exist
    if os.path.isfile(set_file) :
        extract_sets_from_file(set_file)
    # else build the sets
    else :
        print("Building links sets from file : ",links_file," ... ")        
        build_sets_from_file(links_file,prominent_links_file)
        print_sets(set_file)
    set_W()
    print("File read. Found %d articles." %(W))


def build_sets_from_file(links_file,prominent_links_file):
    """Build the links sets from the link list files
    Args:
		links file : file listing all links (both outgoing and incoming) from prominents
		prominent_links_file : file listing the links from prominents
    """
    global Non_Prominents_nb
    # add all the articles from "all_from_prominent" file to the dictionary
    with open(prominent_links_file,'r',encoding='utf-8') as pf:
        for line in pf:
            (title1,title2) = get_article_titles(line)
            add_prominent(title1)
            add_prominent(title2)
    pf.close()
    
    # add all the links to each article 
    regex = r"^(?P<article>[^@]*)@(?P<target>[^\s]*)\s"
    with open(links_file,'r', encoding="utf-8") as f:
        for line in f.readlines():
            link = re.search(regex,line)
            if link is not None:
                article = link.group('article')
                target = link.group('target')
                add_link(article,target)   
    f.close()                
    Non_Prominents_nb = len(Non_Prominents)
    
def extract_sets_from_file(set_file):
    """Extract the links sets from the already existing link sets file
    Args:
	    set_file : input file where sets are stored
    """
    global Non_Prominents_nb
    
    with open(set_file,'r', encoding="utf-8") as f:
        lines  = f.readlines()        
        
        # get nb of non-prominents articles on first line
        nb_regex = r"^(?P<nb>[0-9]+)"    
        first_line = re.search(nb_regex,lines[0])
        if first_line is not None:
            Non_Prominents_nb = float(first_line.group('nb'))
            
        print("Building links sets from file : ",set_file," ... ") 
        set_regex = r"^(?P<article>[^@]*)\t\[(?P<str_set>[^\s]*)\]\s"        
        for line in lines:
            link = re.search(set_regex,line)
            if link is not None:
                article = link.group('article')
                str_set = link.group('str_set')
                extract_links(article,str_set) 
    f.close()                
                                
def print_sets(set_file):
    """Print sets in link set file
    Args:
	    set_file : output file where to store sets
    """
    with open(set_file,'w', encoding="utf-8") as out:
        print("Writing links sets file : ",set_file," ... ") 
        out.write("%d\n"%(Non_Prominents_nb))        
        for article in Links :
            out.write(article+"\t"+string_set(article)+"\n")
    out.close()

def string_set(article) :
    """Fonction to turn a set into string
    Args:
	    article : the prominent article 
    """
    set = Links[article]
    str = "["+set[0]
    for a in set[1:len(set)] :
        str = str+";"+a
    return str+"]"
    
def extract_links(article,str) :
    """Extract all links from a set in links sets file
    Args:
	    article : the prominent article
		str : prominent link set (string as found in link sets file)
    """
    links = str.split(';')
    add_prominent(article)
    for link in links :
        Links[article].append(link)

def add_link(article,target):
    """Add a link "article@target" to the dictionary if the prominent is already stored in it
    Args:
	    article : current article
		target : target of the link
    """
    global Non_Prominents
     
    # add target
    if article in Links.keys():
        if target not in Links[article] :
            Links[article].append(target)
    elif article not in Non_Prominents :
        Non_Prominents.append(article)

    # add article  
    if target in Links.keys():
        if article not in Links[target] :
            Links[target].append(article)
    elif target not in Non_Prominents :
        Non_Prominents.append(target)

        
def add_prominent(article):
    """Add the prominent article to the dictionary
    Args:
	    article : prominent article
    """
    if article not in Links.keys():
        Links[article] = []
        
def get_article_titles(line):
    """ Return the articles titles from a line of the links file
    Args:
	    line : current line
    """
    regex = r"^(?P<article>[^\s]*)\t(?P<target>[^\s]*)"
    link = re.search(regex,line)
    (title1,title2)=("","")
    if link is not None:
        title1 = link.group('article')
        title2 = link.group('target')                           
    return (title1,title2)       
        
def print_all_features(title1,title2):
    """ Return a string of the 3 measures (jaccard,dice,ngd)
    Args:
	    title1 : first article
		title2 : second article
    """
    link_title = title1+"@"+title2     
    jaccard = get_relatedness('j',title1,title2)
    dice = get_relatedness('d',title1,title2)
    ngd = get_relatedness('g',title1,title2)
    return link_title+"\t%f\t%f\t%f" % (jaccard,dice,ngd)+"\n"
    
def print_one_feature(opt,title1,title2):
    """ Return a string of one measure (jaccard,dice or ngd)
    Args:
	    opt : the wanted measure (j:jaccard, d:dice, g:ngd)
	    title1 : first article
		title2 : second article
    """
    link_title = title1+"@"+title2 
    relatedness = get_relatedness(opt,title1,title2)
    return link_title+"\t%f" % (relatedness)+"\n"
    
def print_feature(opt,prominent_links_file,output_file):
    """ Print the feature file
    Args:
	    opt : the wanted measure (j:jaccard, d:dice, g:ngd, a:all)
        prominent_links_file : file listing all links from prominents	
        output_file : new feature file		
    """
    print("Creating new relatedness feature file ...")

    with open(prominent_links_file,'r',encoding='utf-8') as links :    
        with open(output_file,"w",encoding="utf-8") as out:
            for line in links:  
                # get the files names
                (title1,title2) = get_article_titles(line)   
                if opt =='a' :
                    out.write(print_all_features(title1,title2))
                else :
                    out.write(print_one_feature(opt,title1,title2))   
        out.close()
    links.close()

def set_W():
    """ Set W (total number of articles in the set"   """
    global W
    W= len(Links.keys()) + Non_Prominents_nb
    
def get_relatedness(opt,articleA,articleB): 
    """ Return the relatedness of two articles
    Args:
	    opt : the wanted measure (j:jaccard, d:dice, g:ngd)
		articleA : first article
		articleB : second article
    """ 
    set_A = []
    set_B = []    
    if articleA in Links.keys() :
        set_A = Links[articleA]
    if articleB in Links.keys() :
        set_B = Links[articleB]
    
    # Get the option metric
    if opt == 'j':
        return jaccard(set_A,set_B)
    if opt == 'd':
        return dice(set_A,set_B)
    if opt == 'g':
        return normalized_google_distance(set_A,set_B,W)
      
def main():
    try:
        opts,args=getopt.getopt(sys.argv[1:],"jdga",["Jaccard coefficient","Dice's measure","Normalized Google distance","All measures"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        sys.exit(2)

    #  make result directory
    results_dir = "relatedness_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir) 
    
    # build the links sets
    set_file = os.path.join(results_dir,"Links_Sets")
    prominent_links_file = args[1]
    all_links = args[0]
    build_sets(set_file,all_links,prominent_links_file)
    
    title = ""
    stat_file = "" 
    
    # make feature file
    for o,a in opts:
        if o == "-j":
            print_feature('j',prominent_links_file,os.path.join(results_dir,"jaccard_relatedness_feature"))
            stat_file = os.path.join(results_dir,"jaccard_statistics")  
            title = "Jaccard coefficient"
        elif o =="-d":
            print_feature('d',prominent_links_file,os.path.join(results_dir,"dice_relatedness_feature"))
            stat_file = os.path.join(results_dir,"dice_statistics")  
            title = "Dice measure"
        elif o =="-g":
            print_feature('g',prominent_links_file,os.path.join(results_dir,"ngd_relatedness_feature"))
            stat_file = os.path.join(results_dir,"ngd_statistics")
            title = "Normalized Google distance"
        elif o == "-a":
            print_feature('a',prominent_links_file,os.path.join(results_dir,"all_relatedness_features"))
        else :
            assert False,"unhandled option"

    # make stats file and display histogram      
    # Statistics.print_stats(data,stat_file,title)
    
    print("Done. Results stored in : \"",results_dir,"\".")
            
if __name__ == "__main__":
    main()