library(igraph)

# loaded as gi
load("wikigraph_dir")

# loaded as undirgi
load("wikigraph")

# loaded as fc
load("communities_fast_greedy")

# loaded as fc2
load("communities_label_propagation")

# loaded as fc3
load("communities_infomap")


el <- get.edgelist(undirgi)
ids <- V(undirgi)$id
fc1_membership <- fc$membership
fc2_membership <- fc2$membership
fc3_membership <- fc3$membership

edgesdf <- data.frame(
        from=mapply(function(n) {ids[n]}, el[,1]),
        to=mapply(function(n) {ids[n]}, el[,2]),
        same_community_fg=apply(el, 1, FUN=function(row) {if (fc1_membership[row[1]] == fc1_membership[row[2]]) {1} else {-1}}),
        same_community_lp=apply(el, 1, FUN=function(row) {if (fc2_membership[row[1]] == fc2_membership[row[2]]) {1} else {-1}}),
        same_community_im=apply(el, 1, FUN=function(row) {if (fc3_membership[row[1]] == fc3_membership[row[2]]) {1} else {-1}})
)

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
