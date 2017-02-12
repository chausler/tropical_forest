import json
from collections import Counter
from multiprocessing import cpu_count


from gensim import corpora
from gensim.models.wrappers.ldamallet import LdaMallet
from gensim.corpora import Dictionary

MALLET_PATH='/usr/local/Cellar/mallet/2.0.7/bin/mallet'
DATA_PATH = '/Users/ranxiao/Desktop/data/arXiv'

if __name__ == '__main__':
    all_words = []
    ts = 17
    ti = 30
    topic_frequency = []
    dictionary = Dictionary.load(DATA_PATH+'/arxiv_dict.dict')
    for y in range(2000, 2017):
        lst = json.load(open(DATA_PATH+'/processed/processed_{}.json'.format(y)))
        # constructing a document-term matrixcorpus = [dictionary.doc2bow(x) for x in lst]
        mallet = LdaMallet.load(DATA_PATH+'/mallet_files/arxiv_{}_mallet_model'.format(y))
        corpus = [dictionary.doc2bow(x) for x in lst]
        result = mallet[corpus]
        topics = [x[0][0] for x in result]
        counter = Counter(topics)
        topic_frequency_at = [None] * ti
        for i in counter:
            topic_frequency_at[i] = counter[i]
        topic_frequency.append(topic_frequency_at)
    print(topic_frequency)
    json.dump(topic_frequency, open('topic_freqs.json', 'w'))