from math import*
import os, sys,stat
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stat
import re

Sim_Data = []
Jac_Data = []
Dic_Data = []
NGD_Data = []

def extract_data(file):
    global Sim_Data
    global Jac_Data
    global Dic_Data
    global NGD_Data
    rel_regex = r"^(?P<link>[^\s]*)\t(?P<jaccard>[^\s]*)\t(?P<dice>[^\s]*)\t(?P<ngd>[^\s]*)"
    sim_regex = r"^(?P<link>[^\s]*)\t(?P<sim>[^\s]*)\s*$"
    with open(file,'r',encoding='utf-8') as f:
        for l in f.readlines():
            line_sim = re.search(sim_regex,l)
            line_rel = re.search(rel_regex,l)
            if line_sim is not None:
                # link = line_sim.group('link')
                feature = line_sim.group('sim')
                Sim_Data.append(float(feature))
            elif line_rel is not None:
                # link = line.group('link')
                jac_value = line_rel.group('jaccard')
                Jac_Data.append(float(jac_value))
                
                dic_value = line_rel.group('dice')
                Dic_Data.append(float(dic_value))
                
                ngd_value = line_rel.group('ngd')
                NGD_Data.append(float(ngd_value))     
    
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
    
    data = extract_data(file)
    # print_stats(data,"stats_"+title,title)
    
    if Jac_Data :
        print_stats(Jac_Data,"jaccard_statistics","Relatedness histogram(Jaccard coefficient)")

    if Dic_Data :
        print_stats(Dic_Data,"dice_statistics","Relatedness histogram(Dice's measure)")

    if NGD_Data :
        print_stats(NGD_Data,"ngd_statistics","Relatedness histogram(Normalized Google Distance)")
        
    if Sim_Data :
        print_stats(Sim_Data,"Similarity_statistics","Similarity histogram)")
    
if __name__ == "__main__":
    main()