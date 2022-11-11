# TTDS Labs 2022/23 - A Search Engine Course

## Lab 5: Query expansion for search engine queries using Pseudo Relevance Feedback

Retrieving the top 5 ranked terms from the top ranked document for each search query, based on the TFIDF formula, for an improved expanded search query.

### Implementation Overview

1. Pre-processing the given text collection and building an inverted index for it.
2. Parsing the already created Ranked Information Retrieval results (`results.ranked.txt`) for each of the given queries (`queries.lab3.txt`), which are based on the TFIDF formula.
3. Taking the highest ranked document for each query and calculating the TFIDF for each term in that pre-processed document.
4. Retrieving the top 5 terms which are the most relevant terms to expand the original query with, in this case.
5. Parsing and pre-processing the given queries and writing everything to the results file `Qm.1.5.txt`.

### Instructions taken from
https://www.inf.ed.ac.uk/teaching/courses/tts/labs/lab5.html