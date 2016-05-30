#!/bin/bash

# paths to folders
#PROCESSED_DATA='/home/mi8/repo/processed data'
PROCESSED_DATA='.'

# paths to files
PROMINENT_ARTICLES="$PROCESSED_DATA"/prominentArticles_032016_1k.txt
PROMINENT_ARTICLES_NUMBERED="$PROCESSED_DATA"/prominentArticles_032016_1k.txt.numbered
ALL_LINKS_FROM_PROMINENT="$PROCESSED_DATA"/all_links_from_prominent
ALL_LINKS_FROM_PROMINENT_ID_QID="$PROCESSED_DATA"/all_links_from_prominent_id_qid
CLICKSTREAM="$PROCESSED_DATA"/orderedClickList_032016_1k.txt
MISSING_IDS="$PROCESSED_DATA"/missing_ids
LINK_FEATURE="$PROCESSED_DATA"/link_feature
LINK_COUNT_FEATURE="$PROCESSED_DATA"/link_count_feature
SCORES_FEATURE="$PROCESSED_DATA"/scores_feature
SYMMETRIC_FEATURE="$PROCESSED_DATA"/symmetric_feature
COMMUNITIES_FEATURE="$PROCESSED_DATA"/communities_feature
POPULARITY_FEATURE="$PROCESSED_DATA"/popularityFeatures_final.txt
GROUND_TRUTH="$PROCESSED_DATA"/groundtruth_all
GROUND_TRUTH_SORTED="$PROCESSED_DATA"/groundtruth_all.srt
JACCARD="$PROCESSED_DATA"/relatedness/jaccard_relatedness_feature.txt
DICE="$PROCESSED_DATA"/relatedness/dice_relatedness_feature.txt
GOOGLE="$PROCESSED_DATA"/relatedness/google_distance_relatedness_feature.txt
COS_SIM_FEATURE="$PROCESSED_DATA"/cosine_similarity_feature
RANKLIB_TRAINING="$PROCESSED_DATA"/ranklib_training_file
ARFF_HEADER="$PROCESSED_DATA"/arff_header
ARFF="$PROCESSED_DATA"/features.arff

# scripts
TRANSFORM_RANK="$PROCESSED_DATA"/transform_rank.py

#export LANG=en_EN 

sort "$PROMINENT_ARTICLES" | nl -w 1 > "$PROMINENT_ARTICLES_NUMBERED" && \
\
join -2 2 -t $'\t' <(sort -k 1b,1 "$ALL_LINKS_FROM_PROMINENT") <(sort -k 2b,2 "$PROMINENT_ARTICLES_NUMBERED") \
  | sed 's/^\(.*\)\t\(.*\)\t\(.*\)$/\1@\2\tqid:\3/' | sort -k 1b,1 > "$ALL_LINKS_FROM_PROMINENT_ID_QID" && \
\
join -t $'\t' <(tail -n +2 "$CLICKSTREAM" | cut -f 2,3,4 | sed 's/^\(.*\)\t\(.*\)\t\(.*\)$/\1@\2\t\3/' | sort -k 1b,1) \
  "$ALL_LINKS_FROM_PROMINENT_ID_QID" \
  > "$GROUND_TRUTH" && \
\
comm -23 <(cut -f 1 "$ALL_LINKS_FROM_PROMINENT_ID_QID") <(cut -f 1 "$GROUND_TRUTH") > "$MISSING_IDS" && \
\
join -t $'\t' "$ALL_LINKS_FROM_PROMINENT_ID_QID" "$MISSING_IDS" | sed 's/^\(.*\)\t\(qid:.*\)$/\1\t0\t\2/' >> "$GROUND_TRUTH" && \
\
sort -k 1b,1 "$GROUND_TRUTH" > "$GROUND_TRUTH_SORTED" && \
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$LINK_FEATURE") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$LINK_COUNT_FEATURE") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$SCORES_FEATURE") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$SYMMETRIC_FEATURE") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$COMMUNITIES_FEATURE") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$POPULARITY_FEATURE") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$JACCARD") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$DICE") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$GOOGLE") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
join -t $'\t' "$GROUND_TRUTH_SORTED" <(sort -k 1b,1 "$COS_SIM_FEATURE") > "$GROUND_TRUTH_SORTED".tmp &&\
mv "$GROUND_TRUTH_SORTED".tmp "$GROUND_TRUTH_SORTED" &&\
\
cat "$ARFF_HEADER" > "$ARFF" &&\
python3 "$TRANSFORM_RANK" -i "$GROUND_TRUTH_SORTED" -a "$ARFF" -r "$RANKLIB_TRAINING".tmp &&\
sort -k 2bV,2 -k 1n,1 "$RANKLIB_TRAINING".tmp > "$RANKLIB_TRAINING" 
