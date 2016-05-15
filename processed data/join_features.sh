#!/bin/bash

# paths to folders
PROCESSED_DATA='/home/mi8/repo/processed data'

# paths to files
LINK_FEATURE="$PROCESSED_DATA"/link_feature
SCORES_FEATURE="$PROCESSED_DATA"/scores_feature
SYMMETRIC_FEATURE="$PROCESSED_DATA"/symmetric_feature
COMMUNITIES_FEATURE="$PROCESSED_DATA"/communities_feature
POPULARITY_FEATURE="$PROCESSED_DATA"/popularityFeatures_032016_1k.txt
GROUND_TRUTH="$PROCESSED_DATA"/groundtruth_032016_1k.txt
GROUND_TRUTH_SORTED="$PROCESSED_DATA"/groundtruth_032016_1k.txt.srt
JACCARD="$PROCESSED_DATA"/jaccard_relatedness_feature.txt
RANKLIB_TRAINING="$PROCESSED_DATA"/ranklib_training_file

sort -k 2b,2 "$GROUND_TRUTH" > "$GROUND_TRUTH_SORTED" && \
\
join -1 2 -t $'\t' "$GROUND_TRUTH_SORTED" "$LINK_FEATURE" > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" "$SCORES_FEATURE" > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$SYMMETRIC_FEATURE") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" "$COMMUNITIES_FEATURE" > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$POPULARITY_FEATURE") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$JACCARD") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
perl -pe 's/([^@]*)@(.*)\t([0-9][0-9]*)\t (qid:[0-9][0-9]*)\t([0-9][0-9]*)\t([0-9][0-9]*)\t([0-9].*[0-9]*)\t([0-9].*[0-9]*)\t([0-9].*[0-9]*)\t(-*[0-9])\t(-*[0-9])\t(-*[0-9])\t(-*[0-9])\t([0-9][0-9]*)\t([0-9][0-9]*)\t([0-9].*[0-9]*)\t([0-9].*[0-9]*)\t([0-9][0-9]*.*[0-9]*)/$3\t$4\t1:$5\t2:$6\t3:$7\t4:$8\t5:$9\t6:$10\t7:$11\t8:$12\t9:$13\t10:$14\t11:$15\t12:$16\t13:$17\t14:$18\t#$1-->$2/' "$GROUND_TRUTH_SORTED" > "$RANKLIB_TRAINING"
