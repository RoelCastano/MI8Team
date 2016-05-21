from sklearn.feature_extraction.text import TfidfVectorizer
from math import*
import os, sys,stat
import re
import base64
import shutil
import TextParser


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

        
def print_feature(files_dir):
    print("Computing similarity from \"LINKS\" file.")
    lost = 0
    with open(os.path.join(files_dir,"LINKS"),'r',encoding='utf-8') as links:
        with open("cosine_similarity_feature","w",encoding='utf-8') as out:

            # reading links in links file
            regex = r"^(?P<article>[^@]*)@(?P<target>[^\s]*)"
            for line in links:
                link = re.search(regex,line)
                if link is not None:
                    # parsing current article 
                    title1 = link.group('article')
                    filename1 = title1
                    if not os.path.exists(os.path.join(files_dir,filename1)): # the input file name is encoded (b64)
                        filename1 = base64.b64encode(filename1.encode('utf-8')).decode('utf-8')
                       
                    # parsing target article 
                    title2 = link.group('target')
                    filename2 = title2
                  
                    parsed_file_1 = TextParser.parse_file(filename1,files_dir)
                    parsed_file_2 = TextParser.parse_file(filename2,files_dir) 
                    # parsed_file_1 = os.path.join(files_dir,"parsed_files",filename1)
                    # parsed_file_2 = os.path.join(files_dir,"parsed_files",filename2)   
                    
                    # compute feature
                    feature = -1
                    if os.path.exists(parsed_file_1) and os.path.exists(parsed_file_2):                            
                        feature = similarity(parsed_file_1,parsed_file_2)
                    else :
                        lost = lost+1  
                        
                    # writing feature in output file
                    link_title = title1+"@"+title2
                    out.write(link_title+"\t%f\n"%(feature))
                      

        out.close()
    links.close()
    print("Lost links :",lost)    

def main():
    src_files_dir = sys.argv[1]
    parsed_files_dir = os.path.join(src_files_dir,"parsed_files")
    if os.path.exists(parsed_files_dir):
        shutil.rmtree(parsed_files_dir)
    # TextParser.parser(src_files_dir)    
    print_feature(src_files_dir)
    print("Done : results stored in \"cosine_similarity_feature\".")
    
if __name__ == "__main__":
    main()

