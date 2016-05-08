#!/bin/bash

# paths to folders
PROCESSED_DATA='/home/mi8/repo/processed data'
WIKIDUMP=/data/wiki/dumps/latest
WIKIGRAPH=/home/mi8/repo/wikigraph

# paths to files
PROMINENT_ARTICLES="$PROCESSED_DATA"/prominentArticles_032016_1k.txt
PROMINENT_ARTICLES_NUMBERED="$PROCESSED_DATA"/prominentArticles_032016_1k.numbered.txt
PROMINENT_ARTICLES_SORTED="$PROCESSED_DATA"/prominent_articles_sorted 
LIST_OF_DUMPS="$WIKIDUMP"/list_of_dumps
ARTICLES_EXPANDED="$WIKIDUMP"/articles_expanded
ARTICLES_EXPANDED_SORTED="$WIKIDUMP"/articles_expanded_sorted
ARTICLES_INTERSECTION="$WIKIDUMP"/articles_intersection
PROMINENT_INTERSECTION="$WIKIDUMP"/prominent_intersection
PROMINENT_INTERSECTION_NAMED="$WIKIDUMP"/prominent_intersection_named
PROMINENT_INTERSECTION_ALL="$WIKIDUMP"/prominent_intersection_all
PROMINENT_INTERSECTION_OUT="$WIKIDUMP"/prominent_intersection_out
PROMINENT_INTERSECTION_OUT_NAMED="$WIKIDUMP"/prominent_intersection_out_named
PROMINENT_INTERSECTION_OUT_ALL="$WIKIDUMP"/prominent_intersection_out_all
INTERSECTION_GRAPH="$WIKIDUMP"/intersection.graphml
CLICK_LIST="$PROCESSED_DATA"/orderedClickList_032016_1k.txt
ORDERED_CLICK_LIST="$PROCESSED_DATA"/sorted_click_list
SCORES="$WIKIDUMP"/scores
SCORES_FEATURE="$WIKIDUMP"/scores_feature
LINK_FEATURE="$WIKIDUMP"/link_feature
SYMMETRIC_FEATURE="$WIKIDUMP"/symmetric_feature
ALL_LINKS_FROM_PROMINENT="$PROCESSED_DATA"/all_links_from_prominent
COMMUNITIES="$WIKIDUMP"/same_communities
COMMUNITIES_FEATURE="$WIKIDUMP"/communities_feature

# paths to scripts/tools
WIKIGRAPH_PY="$WIKIGRAPH"/wikigraph.py
COMPUTE_GRAPH="$WIKIGRAPH"/compute_graph.R
PROCESS_GRAPH="$WIKIGRAPH"/process_graph.R
FIND_SYMMETRIC="$WIKIGRAPH"/find_symmetric.sh

# expand prominent articles (takes A LOT of time)
#echo "Expanding prominent articles..."
#nice -n 19 python3 "$WIKIGRAPH_PY" -i "$LIST_OF_DUMPS" -s "$PROMINENT_ARTICLES" -o "$ARTICLES_EXPANDED" -d 1

# number prominent articles (queries) by integer numbers > 0 (tab separated)
echo "Numbering prominent articles..."
awk '{printf "%d\t%s\n", NR, $0}' < "$PROMINENT_ARTICLES" > "$PROMINENT_ARTICLES_NUMBERED"

# sort prominent articles
echo "Sorting prominent articles..."
sort "$PROMINENT_ARTICLES" > "$PROMINENT_ARTICLES_SORTED"

# sort clikstream data on the name of the refering article
#echo "Sorting clickstream data..."
#tail -n +2 "$CLICK_LIST" | cut -f 2,3,4 | sed 's/\(.*\)\t\(.*\)\t\(.*\)/\1@\2\t\1\t\2\t\3/' | sort -k 1b,1 > "$ORDERED_CLICK_LIST"

# sort expanded article data
echo "Sorting expanded articles..."
sed 's/^\(.*\)\t\(.*\)\t\(.*\)\t\(.*\)$/\1@\2\t\1\t\2\t\3\t\4/' "$ARTICLES_EXPANDED" | sed '/@\t/d' | sort -k 1b,1 > "$ARTICLES_EXPANDED_SORTED"

# keep only intersection of links
echo "Making intersection..."
join -1 1 -2 2 -t $'\t' "$PROMINENT_ARTICLES_SORTED" <(cut -f 1,2 "$ARTICLES_EXPANDED_SORTED" | sort -k 2b,2) | tee "$PROMINENT_INTERSECTION_OUT" > "$PROMINENT_INTERSECTION"
join -1 1 -2 2 -t $'\t' "$PROMINENT_ARTICLES_SORTED" <(cut -f 1,3 "$ARTICLES_EXPANDED_SORTED" | sort -k 2b,2) >> "$PROMINENT_INTERSECTION"

cut -f 2 "$PROMINENT_INTERSECTION_OUT" | sort -k 1b,1 -u > "$PROMINENT_INTERSECTION_OUT".tmp
cut -f 2 "$PROMINENT_INTERSECTION" | sort -k 1b,1 -u > "$PROMINENT_INTERSECTION".tmp

mv "$PROMINENT_INTERSECTION_OUT".tmp "$PROMINENT_INTERSECTION_OUT"
mv "$PROMINENT_INTERSECTION".tmp "$PROMINENT_INTERSECTION"
join -t $'\t' "$PROMINENT_INTERSECTION_OUT" <(cut -f 1,2,3 "$ARTICLES_EXPANDED_SORTED") > "$PROMINENT_INTERSECTION_OUT_ALL"
join -t $'\t' "$PROMINENT_INTERSECTION" <(cut -f 1,2,3 "$ARTICLES_EXPANDED_SORTED") > "$PROMINENT_INTERSECTION_ALL"

# find article names to the ids
echo "Finding article names to intersection..."
#<---------------------id article1 article2--------------------------------->
join -t $'\t' "$PROMINENT_INTERSECTION_OUT" "$ARTICLES_EXPANDED_SORTED" | cut -f 1,2,3 | sort -k 1b,1 -u > "$PROMINENT_INTERSECTION_OUT_NAMED"
#join -t $'\t' "$PROMINENT_INTERSECTION" "$ARTICLES_EXPANDED_SORTED" | cut -f 1,2,3 > "$PROMINENT_INTERSECTION_NAMED"

# make list of all links from prominent articles
echo "Creating list of all links from prominent articles..."
cut -f 2,3 "$PROMINENT_INTERSECTION_OUT_NAMED" | sort -u > "$ALL_LINKS_FROM_PROMINENT"

# turn information about links into a feature
echo "Preparing link information feature..."
join -t $'\t' "$PROMINENT_INTERSECTION_OUT" <(cut -f 1,4,5 "$ARTICLES_EXPANDED_SORTED") > "$LINK_FEATURE"

# make a graphml representation of links
echo "Making graphml..."
# header and opening graph tags
echo '<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"  
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
    http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <graph id="G" edgedefault="directed">' > "$INTERSECTION_GRAPH"
# main body with edges
cut -f 2,3 "$PROMINENT_INTERSECTION_ALL" | sed 's/"/\&quot;/g' | sed 's/&/\&amp;/g' | sed 's/</\&lt;/g' | sed 's/>/\&gt;/g' | sed 's/^\(.*\)\t\(.*\)$/<edge source="\1" target="\2"\/>/' >> "$INTERSECTION_GRAPH"
# closing tags
echo '  </graph>
</graphml>' >> "$INTERSECTION_GRAPH"

# load graph, compute communities and plot graph (takes A BIT of time)
echo "Computing communities and ploting..."
(cd "$WIKIDUMP" && R CMD BATCH "$COMPUTE_GRAPH")

# load R objects, compute communities and plot graph
echo "Processing communities, hub/authority scores and page rank..."
(cd "$WIKIDUMP" && R CMD BATCH "$PROCESS_GRAPH")

# turn score into a feature
echo "Preparing score feature list..."
#<---------------------------------name id hs as pg --------------------------------------------------------------->
#                           <id and name of referenced article from some of prominent one>                        
join -1 2 -2 1 -t $'\t' <(cut -f 1,3 "$PROMINENT_INTERSECTION_OUT_NAMED" | sort -k 2b,2) <(sed 's/&quot;/"/g' "$SCORES" | sort -k 1b,1) | cut -f 2,3,4,5 | sort -k 1b,1 > "$SCORES_FEATURE"

# turn communities into a feature
echo "Preparing communities feature list..." 
# try both variants for cases where undirected edges are written in opposite direction
join -t $'\t' "$PROMINENT_INTERSECTION_OUT" <(sed 's/^\(.*\)\t\(.*\)\t\(.*\)\t\(.*\)$/\1@\2\t\3\t\4/' "$COMMUNITIES" | sed 's/&quot;/"/g' | sort -k 1b,1)  > "$COMMUNITIES_FEATURE"
join -t $'\t' "$PROMINENT_INTERSECTION_OUT" <(sed 's/^\(.*\)\t\(.*\)\t\(.*\)\t\(.*\)$/\2@\1\t\3\t\4/' "$COMMUNITIES" | sed 's/&quot;/"/g' | sort -k 1b,1) >> "$COMMUNITIES_FEATURE"
sort -k 1b,1 "$COMMUNITIES_FEATURE" > "$COMMUNITIES_FEATURE".tmp
mv "$COMMUNITIES_FEATURE".tmp "$COMMUNITIES_FEATURE"

# symmetric links feature
echo "Finding symmetric links..."
sort -u "$PROMINENT_INTERSECTION_ALL" > "$PROMINENT_INTERSECTION_ALL".uniq
bash "$FIND_SYMMETRIC" "$PROMINENT_INTERSECTION_ALL".uniq "$SYMMETRIC_FEATURE"
