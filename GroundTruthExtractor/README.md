## Scripts for extracting ground truth dataset

# prominentArticles.py
Extracts the most prominent articles from the click stream data. By prominent is ment articles with high number of outgoing clicks. A txt filed is generated with article id's separated with newline

# orderedClickList.py
Generates a list of all the article pairs with (prominent article, linked article) aka (prev, curr), that has popular curr articles: in total 10 >= clicks.

# groundTruth.py
Generated the final ground truth dataset from the orderedClickList and a list containing ALL referenced article from prev-articles. The latter must be generated beforehand from the wiki article dump.