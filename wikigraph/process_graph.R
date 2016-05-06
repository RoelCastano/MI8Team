library(igraph)

# loaded as gi
load("wikigraph_dir")

# loaded as undirgi
load("wikigraph")

# loaded as fc
load("communities_fast_greedy")

# loaded as fc2
load("communities_label_propagation")

el <- get.edgelist(undirgi)

#edgesdf$from <- mapply(function(n) {V(undirgi)[n]$id}, el[,1]) 
edgesdf <- data.frame(from=mapply(function(n) {V(undirgi)[n]$id}, el[,1]))
edgesdf$to <- mapply(function(n) {V(undirgi)[n]$id}, el[,2])
edgesdf$same_community_fg <- apply(el, 1, FUN=function(row) {if (fc$membership[row[1]] == fc$membership[row[2]]) {1} else {-1}})
edgesdf$same_community_lp <- apply(el, 1, FUN=function(row) {if (fc2$membership[row[1]] == fc2$membership[row[2]]) {1} else {-1}})

# write resulting dataframe to the file 
write.table(edgesdf, "same_communities", quote=FALSE, sep='\t', col.names=FALSE, row.names=FALSE)

# compute hub-authority score
hs <- hub_score(gi) 
as <- authority_score(gi)

# compute pagerank
pg <- page_rank(gi)

# make a dataframe with article names
# scoredf <- data.frame(name=V(gi)$id, hub=hs$vector, authority=as$vector, pagerank=pg$vector)
# without e^-17
scoredf <- data.frame(name=V(gi)$id, hub=format(hs$vector, scientific=FALSE), authority=format(as$vector, scientific=FALSE), pagerank=format(pg$vector, scientific=FALSE))

# write resulting datafram to the file
write.table(scoredf, "scores", quote=FALSE, sep='\t', col.names=FALSE, row.names=FALSE)
