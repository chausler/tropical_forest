import json
from collections import Counter
from multiprocessing import cpu_count

from gensim import corpora
from gensim.models.wrappers.ldamallet import LdaMallet
from gensim.corpora import Dictionary

MALLET_PATH='/usr/local/Cellar/mallet/2.0.7/bin/mallet'
DATA_PATH = '../data/hilary'

if __name__ == '__main__':
    all_words = []
    topic_frequency = []
    dictionary = Dictionary.load('hilary_dict.dict')
    for y in range(2009, 2012):
        for m in range(4):
            lst = json.load(open(DATA_PATH+'/processed/processed_{}_{}.json'.format(y, m)))
            mallet = LdaMallet.load(DATA_PATH+'/mallet_files/hilary_{}_{}_mallet_model'.format(y, m))
            corpus = [dictionary.doc2bow(x) for x in lst]
            result = mallet[corpus]
            topics = [x[0][0] for x in result]

            topic_frequency.append(topics)
    print(topic_frequency)
    json.dump(topic_frequency, open('topic_inference.json', 'w'))