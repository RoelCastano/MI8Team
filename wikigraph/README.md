# wikigraph.py


## Description
This script extracts links and texts from articles. It parses Wikipedia dump files, looks for inter-Wikipedia links in articles' text and follows them in expansion.

## Requirements
python >=3.4.4
lxml == 3.5.0
tqdm >= 4.4.1

## Inputs
### dump files
List of dump files in which to search for articles (option -i). List is composed of paths to bzip2 compressed dump files.

### seeds file
List of seeds from which to start breath first search (option -s). List contains article titles separated by new line (one title for one line).

### output file
Path to the file where links will be extracted. There will also be created a new folder texts containing files with article texts.

### depth
Depth of breath first search (option -d). Natural number >0 that means how many hops from seed articles will be expanded.

## Outputs
Extracted links in the output file together with link order (where n indicates that it is nth link in text) and position (number of characters from the beginning).

Also article texts are extracted in separate files for each article.

## How it works
Each dump file is parsed by LXML library. The document tree is kept in memory, but once an element "page" is processed it is removed from the memory. This keeps memory consumption at a reasonable level.

Article text is saved in a file for another feature extraction (file name is base64 encoded article title). It is also scanned with regular expression and every links to another Wikipedia article.

Some links might be linking to redirect pages that does not contain any text and only redirects to regular Wikipedia article with different name. Such redirects are resolved by this script. For example if A links to article B' that redirects to article B, then in the final output there will be only link from A to B.

## Complexity
O(*n*\**d*\**e*) where *n* is the number of pages in all dump files combined, *d* is the depth of expansion and *e* is the number of extracted articles in the output.


# find_symmetric.sh
## Description
This shell script analyses extracted links and looks for symmetric links. A link between articles A and B is considered symmetric if and only if article A links to article B and B links back to A. 

## Requirements
POSIX compliant shell
UNIX core utilities *grep*, *[* and *read*.

## Inputs
### input file
File containing lines in the following format.
> artcile1@article2 article1 article2

Columns might be separated by any white character (e.g space or tab).

### output file
Output containing first column of input file and an indication 1 if link is symmetric or -1 otherwise.

## Outputs
Output containing first column of input file and an indication 1 if link is symmetric or -1 otherwise.

## How it works
For every line, script looks for id with swapped article titles using grep.

## Complexity
O(*n*^2) where *n* is number of lines in the input file.


# compute_graph.R
## Description
This R batch file reads GraphML representation of extracted links in a internal graph representation and runs community detection algorithms.

## Requirements
R
igraph R pacakge

## Inputs
GraphML representation of graph to be processed.

## Outputs
Internal igraph representation of graph on input as both directed and undirected simple graph. igraph object holding informations about communities in simple graph. PDF with color graphical representations of found communities.

## How it works
Graph is read by igraph read.graph function. Then [Fast Greedy](http://igraph.org/r/doc/cluster_fast_greedy.html) and [Label Propagation](http://igraph.org/r/doc/cluster_label_prop.html) algorithms are ran on the resulting simple graph. 

## Complexity
Community detections dominate time complexity of this batch. Fast Greedy algorithm runs in O(|E||V|log|V|) in the worst case, O(|E|+|V|log^2|V|) typically, |V| is the number of vertices, |E| is the number of edges. Label Propagation runs O(|V|+|E|).


# process_graph.R
## Description
This R batch file reads outputs from compute_graph.R and prints indication for each edge, whether both ends are in the same community (1) or not (-1). It also computes Hub and Authority score and Page rank for every vertex.

## Requirements
R
igraph R package

## Inputs
igraph objects containing graph, simple graph, found communities.

## Outputs
Files with indication of the same community for every edge of simple graph and score for every vertex of graph.

## How it works
igraph object are loaded, data frame is constructed and written to a file. [Hub score](http://igraph.org/r/doc/hub_score.html), [Authority score](http://igraph.org/r/doc/authority_score.html) and [Page Rank](http://igraph.org/r/doc/page_rank.html) are computed and written to a file.

## Complexity
Data frame for communities is constructed in O(|E|). Hub and authority score's time complexity depends on the input graph, usually it is O(|V|), the number of vertices. Time complexity of Page rank depends on the input graph, usually it is O(|E|), the number of edges.


# extract_features.sh
## Description
This bash script runs all the previous tools and prepares inputs for them using UNIX core utilities.

## Requirements
Bash shell
UNIX core utilities *awk*, *sort*, *echo*, *sed*, *join*, *cut*, *cd*, *mv*

## How it works
Script runs all the tools above and makes some changes to their output.
