from sklearn.feature_extraction.text import TfidfVectorizer
from math import*
import os, sys

def square_rooted(x):
    return round(sqrt(sum([a*a for a in x])),3)
 
def cosine_similarity(x,y):
    num = sum(a*b for a,b in zip(x,y))
    den = square_rooted(x)*square_rooted(y)
    return round(num/float(den),3)

def similarity(string1,string2):
    # Tf-Idf transformation
    corpus = [article1,article2]
    vectorizer = TfidfVectorizer(min_df=1)
    tfidf_vectors = vectorizer.fit_transform(corpus)
    article_array_1 = tfidf_vectors.toarray()[0]
    article_array_2 = tfidf_vectors.toarray()[1]
    
    return cosine_similarity(article_array_1,article_array_2)
    
with open(sys.argv[1], 'r') as file1:
    article1 = file1.read()
with open(sys.argv[2], 'r') as file2:
    article2 = file2.read()

print('cosine similarity : ',similarity(article1,article2))

 

