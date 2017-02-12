import json
from collections import Counter
from multiprocessing import cpu_count


from gensim import corpora
from gensim.models.wrappers.ldamallet import LdaMallet
from gensim.corpora import Dictionary

MALLET_PATH='/usr/local/Cellar/mallet/2.0.7/bin/mallet'
DATA_PATH = '/Users/ranxiao/Desktop/data/arXiv'

if __name__ == '__main__':
    inferences = json.load(open("topic_inference.json"))
    freqs = []
    for inference in inferences:
        topic_count = Counter(inference)
        topic_count = [topic_count[i] for i in sorted(topic_count.keys())]
        freqs.append(topic_count)
    json.dump(freqs, open("topic_freqs.json", "w"))
