from sklearn.feature_extraction.text import TfidfVectorizer
from math import*
import os, sys,stat
import re
import TextParser


def square_rooted(x):
    return round(sqrt(sum([a*a for a in x])),3)
 
def cosine_similarity(x,y):
    num = sum(a*b for a,b in zip(x,y))
    den = square_rooted(x)*square_rooted(y)
    return round(num/float(den),3)

def similarity(filename1,filename2):
    # read text files
    with open(filename1, 'r',encoding="utf-8") as file1:
        article1 = file1.read()
    # file1.close()
    with open(filename2, 'r',encoding="utf-8") as file2:
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
    print("Computing similarity feature ...")

    with open(os.path.join(files_dir,"LINKS"),'r',encoding='utf-8') as links:
        with open("cosine_similarity_feature","w",encoding="utf-8") as out:

            # reading links in links file
            regex = r"^(?P<article>[^@]*)@(?P<target>[^\s]*)"
            lines  = links.readlines()
            for line in lines:
                link = re.search(regex,line)
                if link is not None:
                    filename1 = link.group('article')
                    filename2 = link.group('target')
                    # parse the 2 files
                    parsed_file_1 = TextParser.parse_file(filename1,files_dir)
                    parsed_file_2 = TextParser.parse_file(filename2,files_dir)
                    # compute feature
                    feature = similarity(parsed_file_1,parsed_file_2)    
                    # writing feature in output file
                    link_title = filename1+"@"+filename2
                    out.write(link_title+"\t%f\n"%(feature))    

        out.close()
    links.close()    

def main():
    src_files_dir = sys.argv[1]
    # TextParser.parser(src_files_dir)
    print_feature(src_files_dir)
    print("Done : results stored in \"cosine_similarity_feature\".")
    
if __name__ == "__main__":
    main()

