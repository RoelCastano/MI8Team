from sklearn.feature_extraction.text import TfidfVectorizer
from math import*
import os, sys,stat
import re
import base64
import shutil
import numpy as np
import TextParser

Histogram = []

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
    # file1.close()
    with open(filename2, 'r',encoding='utf-8') as file2:
        article2 = file2.read()
    # file2.close()
    # Tf-Idf transformation
    corpus = [article1,article2]
    vectorizer = TfidfVectorizer(min_df=1)
    tfidf_vectors = vectorizer.fit_transform(corpus)
    article_array_1 = tfidf_vectors.toarray()[0]
    article_array_2 = tfidf_vectors.toarray()[1]
    
    return cosine_similarity(article_array_1,article_array_2)

def get_article_titles(line):
    regex = r"^(?P<article>[^@]*)@(?P<target>[^\s]*)"
    link = re.search(regex,line)
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
        
def print_feature(files_dir):
    print("Computing similarity from \"LINKS\" file.")
    lost = 0
    with open(os.path.join(files_dir,"LINKS"),'r',encoding='utf-8') as links:
        with open("cosine_similarity_feature","w",encoding='utf-8') as out:
            for line in links:
                (title1,title2) = get_article_titles(line)
                (filename1,filename2) = get_article_names(files_dir,title1,title2)
                # create parsed files
                parsed_file_1 = TextParser.parse_file(filename1,files_dir)
                parsed_file_2 = TextParser.parse_file(filename2,files_dir) 
               
                # compute feature
                feature = -1
                if os.path.exists(parsed_file_1) and os.path.exists(parsed_file_2):                            
                    try :
                        feature = similarity(parsed_file_1,parsed_file_2)
                    except ValueError :
                        # compute similarity on unparsed files
                        feature = similarity(os.path.join(files_dir,filename1),os.path.join(files_dir,filename2))
                else :
                    lost = lost+1  # count number of lost links
                    
                # writing feature in output file
                link_title = title1+"@"+title2
                out.write(link_title+"\t%f\n"%(feature))
                Histogram.append(feature)
        out.close()
    links.close()
    print("Lost links :",lost)    

def print_histogram():
    global Histogram
    hist, bins = np.histogram(Histogram, bins=50)
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hist, align='center', width=width)
    plt.show()      
    
def main():
    src_files_dir = sys.argv[1]
    parsed_files_dir = os.path.join(src_files_dir,"parsed_files")
    if os.path.exists(parsed_files_dir):
        shutil.rmtree(parsed_files_dir)
    # TextParser.parser(src_files_dir)    
    print_feature(src_files_dir)
    print_histogram()
    print("Done : results stored in \"cosine_similarity_feature\".")
    
if __name__ == "__main__":
    main()

