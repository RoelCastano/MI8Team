from math import*
import os, sys,stat
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stat
import re

def extract_data(file):
    regex = r"^(?P<link>[^\s]*)\t(?P<feature>[^\s]*)"
    data=[]
    with open(file,'r',encoding='utf-8') as f:
        for l in f.readlines():
            line = re.search(regex,l)
            if line is not None:
                link = line.group('link')
                feature = line.group('feature')
                data.append(float(feature))
    return data                
    
def print_histogram(data,title):
    hist, bins = np.histogram(data, bins=50)
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hist, align='center', width=width)
    plt.title(title)
    plt.show()
        

def print_stats(data,output_file,title):
    stat_des = stat.describe(np.array(data))
    with open(output_file,'w') as out:
        out.write(str(stat_des))
    print(stat_des)
        
    print_histogram(data,title)

def main():
    file = sys.argv[1]
	title = sys.argv[2]
    data = extract_data(file)
    print_stats(data,"stats_"+title,title)
    
if __name__ == "__main__":
    main()