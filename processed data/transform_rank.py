#!/usr/bin/env python

import pandas as pd
import csv
import getopt
import sys
import re


def main(argv):
    input_name = ''
    arff_name = ''
    rank_name = ''

    try:
        opts, _ = getopt.getopt(argv, "hi:a:r:", ["ifile=", "afile=",
                                                  "rfile=", "help"])
    except getopt.GetoptError:
        print_help()
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-h' or opt == '--help':
            print_help()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_name = arg
        elif opt in ("-a", "--afile"):
            arff_name = arg
        elif opt in ("-r", "--rfile"):
            rank_name = arg

    if input_name == '' or (arff_name == '' and rank_name == ''):
        print_help()
        sys.exit(1)

    input_col_names = ['id', 'rank', 'qid', 'order', 'pos', 'order_log',
                       'pos_log', 'link_count', 'hubscore', 'authorityscore',
                       'pagerank', 'symmetric', 'fc1', 'fc2', 'fc3', 'pop1',
                       'pop2', 'pop3', 'pop4', 'pop5', 'jaccard', 'dice',
                       'google', 'similarity']

    arff_col_names = ['rank', 'rank_norm', 'rank_rank', 'rank_rank_norm',
                      'qid', 'order', 'pos', 'order_log', 'pos_log',
                      'link_count', 'hubscore', 'authorityscore',
                      'pagerank', 'symmetric', 'fc1', 'fc2', 'fc3', 'pop1',
                      'pop2', 'pop3', 'pop4', 'pop5', 'jaccard', 'dice',
                      'google', 'similarity']

    rank_col_names = ['rank_norm', 'qid', 'order', 'pos', 'order_log',
                      'pos_log', 'link_count', 'hubscore', 'authorityscore',
                      'pagerank', 'symmetric', 'fc1', 'fc2', 'fc3', 'pop1',
                      'pop2', 'pop3', 'pop4', 'pop5', 'jaccard', 'dice',
                      'google', 'similarity', 'id_transformed']

    # load groundtruth file
    training = pd.read_csv(input_name, header=None, sep='\t',
                           names=input_col_names)

    # 'rank' clickstream data
    training['rank_rank'] = training[['qid', 'rank']].\
        groupby('qid')['rank'].\
        transform(lambda x: (x.rank(method='dense')))

    # normalise per query
    training['rank_rank_norm'] = training[['qid', 'rank_rank']].\
        groupby('qid')['rank_rank'].\
        transform(lambda x: (x/x.max()))
    training['rank_norm'] = training[['qid', 'rank']].\
        groupby('qid')['rank'].\
        transform(lambda x: (x/x.max()))

    # save results
    if arff_name != '':
        training.to_csv(arff_name, header=None, sep=',', index=False,
                        mode='a', quoting=csv.QUOTE_NONE, quotechar='',
                        columns=arff_col_names, float_format='%.20f')

    if rank_name != '':
        for col_name in rank_col_names[2:-1]:
            training[col_name] = str(rank_col_names.index(col_name)-1) + ':' \
                    + training[col_name].apply(lambda x: '{:.20f}'.format(x))

        id_pattern = re.compile(r'([^@]*)@(.*)')
        training[rank_col_names[-1]] = training['id'].\
            apply(lambda x: '# ' + alter_id(x, id_pattern))

        training.to_csv(rank_name, header=None, sep=' ', index=False,
                        quoting=csv.QUOTE_NONE, quotechar="'", escapechar=' ',
                        columns=rank_col_names, float_format='%.20f')


def alter_id(id_string, id_pattern):
    match = re.match(id_pattern, id_string)
    article_from, article_to = match.groups()
    return article_from + '->' + article_to


def print_help():
    print("""Usage: transform_rank.py -i <inputfile> [-a <arfffile>] [-r <SVM-rankfile>]
This script transforms joined features into final files used in learning or
feature analysis. It can produce @DATA section of ARFF file for Weka and/or
SVM-Rank train file for RankLib and other tools.

Available options:
    -i, --ifile=FILE    path to input file with all features separated by tabs
    -a, --afile=FILE    path to output ARFF file whose @DATA section will be
                        filled
    -r, --rfile=FILE    path to output SVM-rank file
    -h, --help          prints this message""")
    return


if __name__ == "__main__":
    main(sys.argv[1:])
