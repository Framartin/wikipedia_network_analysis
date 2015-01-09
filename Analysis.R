# install.packages("igraph")
library(igraph)

###############################################
#   First solution : pages from categories    #
###############################################

edges = read.csv("data/edges.csv", colClasses = c("character", "character"))
vertex = read.csv("data/vertex.csv", colClasses = c("character", "character", "integer", "character", "character"))
# columns order of the csv : "category","expertneeded","length","name","stub"
# name first
vertex_tmp = vertex[,c(4,5)]
vertex_tmp$expertneeded = vertex$expertneeded
vertex_tmp$category = sub("Category:", "", vertex$category)
vertex_tmp$length = vertex$length
vertex = vertex_tmp
vertex$stub = ifelse(vertex$stub=="True", TRUE, FALSE)
vertex$expertneeded = ifelse(vertex$expertneeded=="True", TRUE, FALSE)

graph <- graph.data.frame(edges, directed=TRUE, vertices=vertex)

# dot file for viz
write.graph(graph, "myGraph.dot", format = "dot")
# gml file for viz
write.graph(graph, "myGraph.gml", format = "gml")


# agregated by categories
category.f <- as.factor(V(graph)$category)
category.nums <- as.numeric(category.f)
graph.c <- contract.vertices(graph, category.nums)
E(graph.c)$weight <- 1
graph.c <- simplify(graph.c)

# selection of edges
summary(E(graph.c)$weight)
hist(E(graph.c)$weight, breaks=50)
sum(E(graph.c)$weight<17)
E(graph.c)$weight[E(graph.c)$weight<10] = 0

category.names <- sort(unique(V(graph)$category))
cat.size <- as.vector(table(V(graph)$category))
plot(graph.c, vertex.size=sqrt(cat.size)/2, vertex.label=category.names, vertex.label.color=rainbow(length(V(graph.c)), alpha=1),
         vertex.color=rainbow(length(V(graph.c)), alpha=0.3), edge.width=sqrt(E(graph.c)$weight)/30,
         edge.arrow.size=0.05, layout=layout.circle, vertex.label.cex=0.7)
# vertex.label.dist=1.5,
# vertex.color=V(graph.c)
# layout : layout.drl layout.kamada.kawai layout.circle

# gml file for viz
write.graph(graph.c, "myGraph_agregated.gml", format = "gml")


# strength /!\ n'a de sens qu'avec des weigth
s_in = graph.strength(graph, mode = 'in')
summary(s_in)
hist(s_in, breaks = 50, col="pink", xlab="Vertex In-Strength", ylab="Frequency", main="")
s_out = graph.strength(graph, mode = 'out')
summary(s_out)
hist(s_out, breaks = 50, col="pink", xlab="Vertex Out-Strength", ylab="Frequency", main="")

##########################################
#   Second solution : pages from list    #
##########################################

# agregated network

edges2_agg = read.csv("data/edges2_aggregated.csv", colClasses = c("character", "character", "integer"))
edges2_agg$from = sub("Category:", "", edges2_agg$from)
edges2_agg$to = sub("Category:", "", edges2_agg$to)

vertex2_agg = read.csv("data/vertex2_aggregated.csv", colClasses = c("character", "integer"))
vertex2_agg$name = sub("Category:", "", vertex2_agg$name)
graph <- graph.data.frame(edges2_agg, directed=TRUE, vertices=vertex2_agg)
vcount(graph)
ecount(graph)
hist(E(graph)$weight, xlim=c(0,1000), breaks=2000, col = "firebrick", xlab = "Poids des liens", main = "")

# graph selection

# size of categories
summary(V(graph)$size)
hist(V(graph)$size, breaks=50, col = "firebrick", xlab="Taille des catégories", main ="")
table(V(graph)$size)
V(graph)$name[V(graph)$size>=61]
sum(V(graph)$size<14)
sum(V(graph)$size<26)
# sélection des 50 plus grands
quantile(V(graph)$size, probs=(1-20/vcount(graph))) # 26 pour 50 vertices, 50 pour 30 vertices, 61 pour 20 vertices

# selection of vertex
vertex_to_delete = V(graph)[V(graph)$size<61] # médiane = 14
graph = graph - vertex_to_delete

# weights
summary(E(graph)$weight)
hist(E(graph)$weight, breaks=50)
sum(E(graph)$weight<7)

# selection of edges
length(E(graph)$weight[E(graph)$weight>=364.0]) # ou 68
edges_to_delete = E(graph)[E(graph)$weight<364.0]

# we reduce our graph

graph = graph - edges(edges_to_delete)

vcount(graph)
ecount(graph)

cat.size <- V(graph)$size
plot(graph, vertex.size=sqrt(cat.size)/1.2, vertex.label=V(graph)$name, vertex.label.color="black",
     vertex.color=rainbow(length(V(graph)), alpha=0.3), edge.width=sqrt(E(graph)$weight)/20,
     edge.arrow.size=0.3, layout=layout.kamada.kawai, vertex.label.cex=1)
# vertex.label.dist=1.5,
# vertex.color=V(graph.c)
# layout : layout.drl layout.kamada.kawai layout.circle layout.fruchterman.reingold
# vertex.label.color=rainbow(length(V(graph)), alpha=1)

#########################
# non-agregated network

edges2 = read.csv("data/edges2.csv", colClasses = c("character", "character"))
vertex2 = read.csv("data/vertex2.csv", colClasses = c("character", "integer", "character", "character"))
# name first
vertex2_tmp = vertex2[,3:4]
vertex2_tmp$expertneeded = vertex2$expertneeded
vertex2_tmp$length = vertex2$length
vertex2 = vertex2_tmp
rm(vertex2_tmp)
vertex2$stub = ifelse(vertex2$stub=="True", TRUE, FALSE)
vertex2$expertneeded = ifelse(vertex2$expertneeded=="True", TRUE, FALSE)

graph <- graph.data.frame(edges2, directed=TRUE, vertices=vertex2)

# enlever 'List of' et 'Outline'
vertex_to_delete = V(graph)[V(graph)$name[grepl("Outline",V(graph)$name)]]
graph = graph - vertex_to_delete
vertex_to_delete = V(graph)[V(graph)$name[grepl("List of|Lists of",V(graph)$name)]]
graph = graph - vertex_to_delete



# dot file for viz
write.graph(graph, "myGraph2.dot", format = "dot")
# gml file for viz
write.graph(graph, "myGraph2.gml", format = "gml")


#plot(graph)
#igraph.options(vertex.size=3, vertex.label=NA,
#               edge.arrow.size=0.5)
#plot(graph, layout=layout.circle)
#title("5x5x5 Lattice")
#plot(graph, layout=layout.fruchterman.reingold)
#title("Blog Network")



# absence of loops and multi-edges
is.simple(graph)

vcount(graph)
ecount(graph)
neighbors(graph,5)


# degrees
# question : heterogeneous ?
d_in = degree(graph, mode="in")
summary(d_in)
hist(d_in, breaks = 50, col="lightblue", xlab="Degré entrant des sommets", ylab="Fréquence", main="")
hist(d_in, breaks = 50, col="lightblue", xlab="Degré entrant des sommets", ylab="Fréquence", main="", xlim = c(0,600))
# très élevé
sort(d_in[d_in > 600], decreasing=T)
# 1er pic
sort(d_in[d_in > 450 & d_in <= 600 ], decreasing=T)
# 2e
sort(d_in[d_in > 250 & d_in <= 450 ], decreasing=T)
# 3em pic : les distributions
sort(d_in[d_in > 150 & d_in <= 250 ], decreasing=T)
# question : est-ce que ça correspond à ce qui est fondamental en stat ?
# qu'est-ce qui caractérise ce qui fait le plus référence en stat sur wikipedia ?


d_out = degree(graph, mode="out")
summary(d_out)
hist(d_out, breaks = 50, col="lightblue", xlab="Degré sortant des sommets", ylab="Fréquence", main="")

# on a des points d'entrée dans la stat comme "Epidemiology", "Econometrics"
sort(d_out[d_out > 350], decreasing=T)
# 1er pic
sort(d_out[d_out > 220 & d_out <= 350 ], decreasing=T)
# 2iem pic : les distributions
sort(d_out[d_out > 160 & d_out <= 220 ], decreasing=T)


# log degree
par(mfrow = c(1,2))
dd_in <- degree.distribution(graph, mode="in")
d <- 1:max(d_in)-1
ind <- (dd_in != 0)
d[1]=0.3 # we add an epsilon to the 0 in-degree
plot(d[ind], dd_in[ind], log="xy", col="blue",
     xlab=c("In-Degree (log-scale)"), ylab=c("Intensity (log-scale)"),
     main="Log-Log In-Degree Distribution")

dd_out <- degree.distribution(graph, mode="out")
d <- 1:max(d_out)-1
outd <- (dd_out != 0)
d[1]=0.3 # we add an epsilon to the 0 out-degree
plot(d[outd], dd_out[outd], log="xy", col="blue",
     xlab=c("Log-Out-Degree"), ylab=c("Log-Intensity"),
     main="Log-Log Out-Degree Distribution")

# hexbin viz
library(hexbin)
# in
x <- log(d[ind])
y <- log(dd_in[ind])
bin<-hexbin(x, y, xbins=50)
plot(bin, main="Hexagonal Binning") 
# out
x <- log(d[outd])
y <- log(dd_out[outd])
bin<-hexbin(x, y, xbins=50)
plot(bin, main="Hexagonal Binning") 

# in + out degree
d_total <- degree(graph, mode="total")


## understand the manner in which vertices of different degrees are linked with each other.
# average degree of the neighbors of a given vertex
# in + out degree
a.nn.deg <- graph.knn(graph,V(graph))$knn
plot(d_total, a.nn.deg, col="goldenrod", xlab=c("Vertex Degree"),
     ylab=c("Degré moyen des voisins"))
plot(d_total, a.nn.deg, log="xy", col="goldenrod", xlab=c("Log Vertex Degree"),
     ylab=c("Degré moyen des voisins"))
# Average neighbor degree versus vertex degree (log–log scale)


x <- log(d_total)
y <- log(a.nn.deg)
bin<-hexbin(x, y, xbins=50)
plot(bin, main="", xlab=c("Log du degré des sommets"), ylab=c("Log du degré moyen des voisins") ) 


# correlation between degree and size

cor(d_in,V(graph)$length)
cor(log(d_in[d_in!=0]),log(V(graph)$length[d_in!=0]))

plot(d_in, V(graph)$length, col="firebrick", xlab=c("Degré entrant"),
     ylab=c("Taille en octets"))
plot(d_in, V(graph)$length, log="xy", col="firebrick", xlab=c("Degré entrant (log)"),
     ylab=c("Taille en octets (log)"))

x <- log(d_in+0.3)
y <- log(V(graph)$length)
bin<-hexbin(x, y, xbins=50)
plot(bin, main="", xlab=c("Log du degré des sommets"), ylab=c("Log du degré moyen des voisins") ) 

# sortant
cor(d_out,V(graph)$length)
plot(d_out, V(graph)$length, col="firebrick", xlab=c("Degré entrant (log)"),
     ylab=c("Taille en octets (log)"))
plot(d_out, V(graph)$length, log="xy", col="firebrick", xlab=c("Degré entrant (log)"),
     ylab=c("Taille en octets (log)"))

x <- log(d_out+0.3)
y <- log(V(graph)$length)
bin<-hexbin(x, y, xbins=50)
plot(bin, main="", xlab=c("Log du degré des sommets"), ylab=c("Log du degré moyen des voisins"), col = "firebrick" ) 


# stub et expertneeded en fonction des degrees / de la taille / des clusters trouvés
length(V(graph)$name[V(graph)$stub])
V(graph)$name[V(graph)$stub]

summary(V(graph)$length[V(graph)$stub])

A = V(graph)$length[V(graph)$stub]
B = V(graph)$length[!V(graph)$stub]
mean(A, na.rm=T) ; mean(B, na.rm=T)
median(A,na.rm=T) ; median(B, na.rm=T)
boxplot(A,B)
t.test(A, B) # par d?faut il fait comme si sigma1 diff?rent de signma2

# idem avec deg in
A = d_in[V(graph)$stub]
B = d_in[!V(graph)$stub]
mean(A, na.rm=T) ; mean(B, na.rm=T)
median(A,na.rm=T) ; median(B, na.rm=T)
boxplot(A,B)
t.test(A, B)


# expertneeded
length(V(graph)$name[V(graph)$expertneeded])
V(graph)$name[V(graph)$expertneeded]

A = d_in[V(graph)$expertneeded]
B = d_in[!V(graph)$expertneeded]
mean(A, na.rm=T) ; mean(B, na.rm=T)
median(A,na.rm=T) ; median(B, na.rm=T)
boxplot(A,B)
t.test(A, B)



# the graph is not connected

is.connected(graph, mode="weak")
# A digraph G is weakly connected if its underlying graph (i.e., the result of stripping away the labels ‘tail’ and ‘head’ from G ) is connected.

is.connected(graph, mode="strong") 
#It is called strongly connected if every vertex v is reachable from every u by a directed walk.

# nb of clusters
no.clusters(graph)

# there is only 19 vertice not in the main cluster
clusters(graph, mode="strong")
clusters(graph, mode="weak") # par défaut : weak
V(graph)[clusters(graph, mode="weak")$membership!=1]

# network cohesion
# cliques length /!\ undirected graph
table(sapply(cliques(graph), length))
# dyad
dyad.census(graph)
# Two fundamental quantities, going back to early work in social network analysis, are dyads and triads. Dyads are
# pairs of vertices and, in directed graphs, may take on three possible states: null (no directed edges), 
# asymmetric (one directed edge), or mutual (two directed edges).
triad.census(graph)
?triad.census
plot(triad.census(graph), ylim = c(0,5e6))

# propotion of reciprocal edges
# the probability that the opposite counterpart of a directed edge is also included in the graph
reciprocity(graph)

# density
graph.density(graph)
# The density of a graph is the frequency of realized edges relative to potential edges.
# The value of den(H) will lie between zero and one and provides a measure of how close H is to being a clique.




# principal connected component
#vertex_to_delete = V(graph)[clusters(graph, mode="weak")$membership!=1]
#graph = graph - vertex_to_delete


# Centrality measure
# closeness
c.graph = closeness(graph, mode = "in") # using path TO a vertex
head(c.graph[order(c.graph, decreasing=T)], n=50)

# betweenness
b.graph = betweenness(graph)
head(b.graph[order(b.graph, decreasing=T)], n=50)


# eigenvector centrality
evcent(graph, directed=T)$vector
evcent(graph, directed=T)$value

# Hubs
h.graph = hub.score(graph)$vector
head(h.graph[order(h.graph, decreasing=T)], n=50)

# Authorities
a.graph = authority.score(graph)$vector
head(a.graph[order(a.graph, decreasing=T)], n=50)



# acyclic ? (no cycles ?)
is.dag(graph)
# nb of cycles ?

# adjacency matrix
#get.adjacency(graph)


diameter(graph, weights=NA) 


# partitioning
comps <- decompose.graph(graph)
table(sapply(comps, vcount))

# keep the giant component
graph.gc <- decompose.graph(graph)[[1]] # weak mode

# small world ? YES
average.path.length(graph.gc)
diameter(graph.gc) # not so big
transitivity(graph.gc) # high clustering coefficient

vertex.connectivity(graph.gc)
edge.connectivity(graph.gc)




# graph partitioning
kc <- fastgreedy.community(graph.gc)
length(kc)
sizes(kc)
membership(kc)
plot(kc,karate)

library(ape)
dendPlot(kc,mode="phylo")

# spectral partitioning
g.lap <- graph.laplacian(graph)
eig.anal <- eigen(g.lap)
plot(Re(eig.anal$values), col="blue", ylab="Eigenvalues of Graph Laplacian")
tail(eig.anal$values, n = 100)
f.vec <- eig.anal$vectors[, length(eig.anal$values)-75]
f.vec <- eig.anal$vectors[, length(eig.anal$values)-1]

faction <- get.vertex.attribute(graph, "Faction")
f.colors <- as.character(length(faction))
f.colors[faction == 1] <- "red"
f.colors[faction == 2] <- "cyan"
plot(Re(f.vec), pch=16, xlab="Actor Number",
     ylab="Fiedler Vector Entry") #col=f.colors)
abline(0, 0, lwd=2, col="lightgray")


comm = leading.eigenvector.community(graph.gc)
table(comm$membership)
table(table(comm$membership))
V(graph.gc)$name[comm$membership==1]
V(graph.gc)$name[comm$membership==3] # distribution ; tmp = V(graph.gc)$name[comm$membership==3] ; sum(grepl("distribution", tmp))/length(tmp)
V(graph.gc)$name[comm$membership==4] # theorem ; stats-maths ; 
V(graph.gc)$name[comm$membership==5] # softwares
V(graph.gc)$name[comm$membership==6]
V(graph.gc)$name[comm$membership==7]
V(graph.gc)$name[comm$membership==8] # biais
for (i in 9:16) { print(i) ; print(V(graph.gc)$name[comm$membership==i]) }


#g.full <- graph.full(7)
#g.ring <- graph.ring(7)
#g.tree <- graph.tree(7, children=2, mode="undirected")
#g.star <- graph.star(7, mode="undirected")
# par(mfrow=c(2, 2))
# plot(g.full)
# plot(g.ring)
# plot(g.tree)
# plot(g.star)

