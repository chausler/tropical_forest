import json
from gensim import corpora
from gensim.models.wrappers.ldamallet import LdaMallet
from multiprocessing import cpu_count

MALLET_PATH='/usr/local/Cellar/mallet/2.0.7/bin/mallet'
DATA_PATH = '../data/arXiv'

if __name__ == '__main__':
    entire_corpus = []
    for y in range(2000, 2017):
        lst = json.load(open(DATA_PATH+'/processed/processed_{}.json'.format(y)))
        entire_corpus.extend(lst)
        # constructing a document-term matrix
    dictionary = corpora.Dictionary(entire_corpus)
    dictionary.filter_extremes(5, 0.1)
    dictionary.save(DATA_PATH+'/arxiv_dict.dict')
    dictionary = corpora.Dictionary.load(DATA_PATH+'/arxiv_dict.dict')
    for y in range(2000, 2017):
        print(y)
        lst = json.load(open(DATA_PATH + '/processed/processed_{}.json'.format(y)))
        # print(dictionary)
        corpus = [dictionary.doc2bow(x) for x in lst]

        lda = LdaMallet(
            mallet_path=MALLET_PATH,
            corpus=corpus,
            id2word=dictionary,
            num_topics=30,
            optimize_interval=10,
            iterations=2000,
            workers=cpu_count(),
        )
        lda.save(DATA_PATH+'/mallet_files/arxiv_{}_mallet_model'.format(y))