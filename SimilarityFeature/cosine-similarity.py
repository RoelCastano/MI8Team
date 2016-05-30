from sklearn.feature_extraction.text import TfidfVectorizer
from math import*
import os, sys,stat
import re
import base64
import shutil
import numpy as np
import TextParser
# import Statistics

# data =[]

def square_rooted(x):
    return round(sqrt(sum([a*a for a in x])),3)
 
def cosine_similarity(x,y):
    num = sum(a*b for a,b in zip(x,y))
    den = square_rooted(x)*square_rooted(y)
    return round(num/float(den),3)

def similarity(filename1,filename2):
    # read text files
    with open(filename1, 'r',encoding='utf-8') as file1:
        article1 = file1.read()
    file1.close()
    with open(filename2, 'r',encoding='utf-8') as file2:
        article2 = file2.read()
    file2.close()
    # Tf-Idf transformation
    corpus = [article1,article2]
    vectorizer = TfidfVectorizer(min_df=1)
    tfidf_vectors = vectorizer.fit_transform(corpus)
    article_array_1 = tfidf_vectors.toarray()[0]
    article_array_2 = tfidf_vectors.toarray()[1]
    
    return cosine_similarity(article_array_1,article_array_2)

def get_article_titles(line):
    regex = r"^(?P<article>[^\s]*)\t(?P<target>[^\s]*)"
    link = re.search(regex,line)
    (title1,title2)=("","")
    if link is not None:
        title1 = link.group('article')
        title2 = link.group('target')                           
    return (title1,title2)         

def get_article_names(files_dir,title1,title2) :
    filename1 = title1
    filename2 = title2
    if not os.path.exists(os.path.join(files_dir,filename1)): # the input file name is encoded (b64)
        filename1 = base64.b64encode(filename1.encode('utf-8')).decode('utf-8')
        
    if not os.path.exists(os.path.join(files_dir,filename1)): # the input file name is encoded (b64)
        filename2 = base64.b64encode(filename2.encode('utf-8')).decode('utf-8')
    return (filename1,filename2)    
        
def print_feature(files_dir,parsed_files_dir,results_dir,links_file):
    print("Computing similarity from \"LINKS\" file.")
    lost = 0
    
    # Reading the links file (all outgoing and incoming links from prominent articles)  
    with open(links_file,'r',encoding='utf-8') as links:
        with open(os.path.join(results_dir,"cosine_similarity_feature"),"w",encoding='utf-8') as out:
            
            # nb_lines = 0
            
            for line in links:  
                # get the files names (and encode in base64 if necessary)
                (title1,title2) = get_article_titles(line)
                (filename1,filename2) = get_article_names(files_dir,title1,title2)
                
                # create parsed files 
                parsed_file_1 = TextParser.parse_file(filename1,files_dir,parsed_files_dir)
                parsed_file_2 = TextParser.parse_file(filename2,files_dir,parsed_files_dir)
                
                # compute feature
                feature = -1
                if os.path.isfile(parsed_file_1) and os.path.isfile(parsed_file_2):                            
                    try :
                        feature = similarity(parsed_file_1,parsed_file_2)
                    except ValueError :
                        # compute similarity on unparsed files
                        src_file1 = os.path.join(files_dir,filename1)
                        src_file2 = os.path.join(files_dir,filename2)
                        if os.path.isfile(src_file1) and os.path.isfile(src_file2) :
                            feature = similarity(src_file1,src_file2)
                        else :
                            feature =-1
                            lost = lost+1
                else :
                    lost = lost+1  # count number of lost links
                    
                # write feature in output file
                link_title = title1+"@"+title2
                out.write(link_title+"\t%f\n"%(feature))
                # data.append(feature)
        out.close()
    links.close()
    print("Lost links :",lost)         
    
def main():
    src_files_dir = sys.argv[1]
    links_file = sys.argv[2]
    
    parsed_files_dir = os.path.join(src_files_dir,"parsed_files")
    if os.path.exists(parsed_files_dir):
        shutil.rmtree(parsed_files_dir)
    
    results_dir = os.path.join(src_files_dir,"cosine_similarity_results")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # TextParser.parser(src_files_dir)    
    print_feature(src_files_dir,parsed_files_dir,results_dir,links_file)
    
    print("Done : results stored in \"",results_dir,"\".")
    
    ## Display and save statistics
    # stat_file = os.path.join(results_dir,"cosine_similarity_statistics")
    # Statistics.print_stats(data,stat_file,"Cosine similarity")
    
if __name__ == "__main__":
    main()

