# Processed datasets
### prominentArticles_032016_1k
contains names / ID's for articles in wiki with the highest outgoing clicks to other articles. It contains coloumns (separated by tab):
1. ID of article

### orderedClickList_032016_1k
contains data on pairs of articles (A,B) where article A is one of the articles in prominentArticles_032016_1k and B is an article it links to. It contains coloumns (separated by tab):
1. rank, for use later in ranklib file
2. prev, ID of one of the prominent articles
3. curr, ID of an article linked to by prev
4. clicks, number of visitors clicking the link represented by this row