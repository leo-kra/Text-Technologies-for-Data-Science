import json
import math
import re
import time
import xml.etree.ElementTree as ET

import np as np
from stemming.porter2 import stem


def parse_stopwords():  # get list of all stopwords
    with open('englishST.txt', 'r') as f:
        return [line.split('\n')[0] for line in f.readlines()]


def tokenisation(text):  # split on every non-letter character
    tokens = re.compile(r'(\w{0,})').findall(text)
    tokens = [word for word in tokens if word != '']
    return tokens


def lower_stopping_normalise(text, stop_words):
    text = [word.lower() for word in text]  # make lowercase
    text = [word for word in text if word not in stop_words]  # remove stop words
    text = [stem(word) for word in text]  # normalise / Porter stemming
    return text


def build_index():
    start = time.time()

    file = 'collections/trec.sample.xml'
    tree = ET.parse(file)
    root_xml = tree.getroot()

    stop_words = parse_stopwords()
    totalNum = 0

    unique = {}

    for document in root_xml.findall('DOC'):  # <DOC> is where a new document begins
        docNo = document.find('DOCNO').text  # get the document ID
        headline = document.find('HEADLINE').text  # get the headline
        text = document.find('TEXT').text  # get the main body text
        totalNum += 1

        full_text = headline + ' ' + text  # combine headline and text fields

        tokenised = tokenisation(full_text)
        stopped = lower_stopping_normalise(tokenised, stop_words)

        for idx, t in enumerate(stopped):
            pos = idx + 1  # start indexing at 1 and not 0

            # unique = dict(sorted(unique.items(), key=lambda item: item[0]))

            if unique.get(t) is not None:  # word already exists
                occurrence, count = unique[t]  # get stored values

                if occurrence.get(docNo) is not None:  # same word appears again in same file
                    occurrence[docNo].append(pos)  # append another word position
                    unique[t] = (occurrence, count)  # file counter stays the same
                else:  # new unique file for that word
                    occurrence[docNo] = [pos]  # store at which position the word appeared in that file
                    unique[t] = (occurrence, count + 1)  # increase the counter of number of file appearances

            else:  # new unique word
                occurrence = {docNo: [pos]}  # new dictionary with doc num and position of word
                unique[t] = (occurrence, 1)  # add new unique word and number of file appearances

    end = time.time()
    duration = end - start
    print(f'Duration for building and writing index: {duration}')

    return unique


def write_txt(dic):
    with open('index.txt', 'w') as f:
        for key, value in dic.items():
            occurrence, count = value

            f.write(key + ":" + str(count))
            f.write("\n")

            for key2, value2 in occurrence.items():
                f.write("\t" + key2 + ": " + ",".join(str(x) for x in value2))
                f.write("\n")

            f.write("\n")


def json_dump(dic):
    with open('index.json', 'w') as f:
        json.dump(dic, f)


def get_docs(num):
    with open('results.ranked.txt', 'r') as f:
        data = f.readlines()

    results = []
    result = [result.strip('\n').split(',') for result in data]
    results.extend(result)

    bool = True
    for r in results:
        if int(r[0]) == num and bool:  # take only the top document
            return r


def get_TFIDF(docNo, N, text):
    dict = {}
    for word in text:
        tf = 0  # tf(t,d) = number of times term t appeared in document d
        df = 0  # df(t) = number of documents term t appeared in

        with open('index.json', 'r') as f:
            data = json.load(f)

            for key, value in data.items():
                occurrence, count = value
                if key == word:
                    df = str(count)  # get df
                    for key2, value2 in occurrence.items():
                        if key2 == docNo:
                            tf = len(value2)  # get tf

        tfidf = tf * math.log(N / int(df), 10)  # tfidf = tf*log(N/df)
        dict[word] = tfidf

    sorted_tfidf = []
    sorted_tfidf = sorted(dict.items(), key=lambda item: item[1], reverse=True)

    return sorted_tfidf[:5]  # get top 5 TFIDF terms for each query


def get_query(queryNum):
    with open('queries.lab3.txt', 'r') as f:
        for i, line in enumerate(f):
            if i == queryNum - 1:
                tokens = tokenisation(line)
                stopped = lower_stopping_normalise(tokens, parse_stopwords())
                return stopped[1:]


def main():  # Read the results file and extract the numbers of top n_d ranked documents
    nums = np.arange(1, 11)
    for num in nums:  # get the top ranked result for each query
        doc = get_docs(num)
        search_docNum = doc[1]

        file = 'collections/trec.sample.xml'
        tree = ET.parse(file)
        root_xml = tree.getroot()

        stop_words = parse_stopwords()
        stopped = ''
        N = 0

        for document in root_xml.findall('DOC'):  # <DOC> is where a new document begins
            docNo = document.find('DOCNO').text  # get the document ID
            headline = document.find('HEADLINE').text  # get the headline
            text = document.find('TEXT').text  # get the main body text
            N += 1

            full_text = headline + ' ' + text  # combine headline and text fields

            if docNo == search_docNum:
                tokenised = tokenisation(full_text)
                stopped = lower_stopping_normalise(tokenised, stop_words)
                # break -> not for now to get number of total documents
                N = 1000  # shortcut for now
                results_dic = get_TFIDF(docNo, N, stopped)

                words = [word for word, tfidf in results_dic]
                query = get_query(int(doc[0]))

                with open('Qm.1.5.txt', 'a') as f:
                    f.write(f'{query} + {words}')
                    f.write("\n")


if __name__ == '__main__':
    # dic = build_index()
    # write_txt(dic)
    # json_dump(dic)
    main()  # PRF can suggest useful terms for query expansion
