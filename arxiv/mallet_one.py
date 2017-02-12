import json
from gensim import corpora
from gensim.models.wrappers.ldamallet import LdaMallet
from multiprocessing import cpu_count

MALLET_PATH='/usr/local/Cellar/mallet/2.0.7/bin/mallet'
DATA_PATH = '../data/arXiv/mallet_files'
# For debuggering


if __name__ == '__main__':
    # lst = json.load(open('tmp.json'))
    # print(lst)
    # dictionary = corpora.Dictionary(lst)
    # dictionary.filter_extremes(5, 0.1)
    # corpus = [dictionary.doc2bow(x) for x in lst]
    #
    # lda = LdaMallet(
    #     mallet_path=MALLET_PATH,
    #     corpus=corpus,
    #     id2word=dictionary,
    #     num_topics=30,
    #     optimize_interval=10,
    #     iterations=2000,
    #     workers=cpu_count(),
    # )
    lda = LdaMallet.load(DATA_PATH+'/arxiv_2013_mallet_model')
    for i in range(30):
        print([x for x,p in lda.show_topic(i,num_words=15)])

