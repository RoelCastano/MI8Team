library(igraph)

# parse graph from graphml
gi <- read.graph("intersection.graphml", "graphml")

# make symmetrisation of the graph
undirgi = simplify(as.undirected(gi))

# save both graphs
save(gi, file="wikigraph_dir")
save(undirgi, file="wikigraph")

# define pallete for community coloring
mypallete = function(count, n) {rainbow(count)[n]}

# compute communities the first way
fc <- cluster_fast_greedy(undirgi)

# save computed communities into a file
save(fc, file="communities_fast_greedy")

# compute communities the second way
fc2 <- cluster_label_prop(undirgi)

# save computed communities into a file
save(fc2, file="communities_label_propagation")

# set plot options
igraph.options(vertex.size=2, edge.width=0.1, vertex.label=NA)

# color vertices according to the membership to community (fast_greedy)
V(undirgi)$color <- mapply(mypallete, length(fc), fc$membership)

# plot graph with communities visualised
pdf("wikiplot_fast_greedy.pdf", 100, 100); plot(undirgi); dev.off()

# color vertices according to the membership to community (label_propagation)
V(undirgi)$color <- mapply(mypallete, length(fc2), fc2$membership)

# plot graph with communities visualised
pdf("wikiplot_label_propagation.pdf", 100, 100); plot(undirgi); dev.off()
