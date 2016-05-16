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
    with open(filename2, 'r',encoding="utf-8") as file2:
        article2 = file2.read()
    # Tf-Idf transformation
    corpus = [article1,article2]
    vectorizer = TfidfVectorizer(min_df=1)
    tfidf_vectors = vectorizer.fit_transform(corpus)
    article_array_1 = tfidf_vectors.toarray()[0]
    article_array_2 = tfidf_vectors.toarray()[1]
    
    return cosine_similarity(article_array_1,article_array_2)

        
def print_feature(parsed_files_dir):
    print("Computing similarity feature ...")
    files = os.listdir(parsed_files_dir)
    files = os.listdir(parsed_files_dir)
    with open("cosine_similarity_feature","w",encoding="utf-8") as out:
        seen_couples = []
        for filename1 in files:
            file1 = os.path.join(parsed_files_dir,filename1)
            for filename2 in files :
                if (filename2,filename1) not in seen_couples and filename1 != filename2:
                    # printing feature in a new text file
                    file2 = os.path.join(parsed_files_dir,filename2)
                    feature = similarity(file1,file2)                    
                    # writing both article1@article2 and article2@article similarity feature                     
                    link_title1 = filename1+"@"+filename2
                    out.write(link_title1+"\t%f\n"%(feature))    
                    link_title2 = filename2+"@"+filename1
                    out.write(link_title2+"\t%f\n"%(feature))
                    
                    # marking the couple as seen
                    seen_couples.append((filename1,filename2))
    out.close()    

def main():
    src_files_dir = sys.argv[1]
    parsed_files_dir = TextParser.parser(src_files_dir)
    print_feature(parsed_files_dir)
    print("Done : results stored in \"",os.path.join("parsed_files","cosine_similarity_feature"),"\"")
    
if __name__ == "__main__":
    main()

