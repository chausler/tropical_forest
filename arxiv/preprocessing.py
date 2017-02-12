"""
Assume input is a lst of strings
"""
__author__ = 'Ran Xiao'
# built in
import time
import json
from functools import partial
from collections import Counter
from multiprocessing import Pool, cpu_count

# 3rd-party
from nltk.tokenize import RegexpTokenizer, sent_tokenize
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer

# my code
import entry

# Constants
NOUN_TYPES = ('NN','NNS','NNP','NNPS')
word_tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
DATA_PATH = '/Users/ranxiao/Desktop/data/arXiv'

# Acquired resources
lemmatizer = WordNetLemmatizer()


def predoc(text):
    """
    turn text into a list of tokens aka list of string for lda
    :param text:
    :return:
    """
    result = []
    for sent in sent_tokenize(text):
        # tokenize words
        words = [word for word in word_tokenizer.tokenize(sent)]
        # get sent components
        sent_components = pos_tag(words)
        # lemmatization the case information helps the lemmatization.
        sent_components = [(lemmatizer.lemmatize(w), t) if t in NOUN_TYPES else (w, t) for (w, t) in sent_components]
        # merge
        sent_components = merge_components(sent_components)
        # get only nouns
        nouns = [w for w, t in sent_components if t in NOUN_TYPES]

        result.extend(nouns)
    # get lower
    return [x.lower() for x in result]


def find_ngrams(lst_str, threshold=0.1, minimum=5):
    word_freq = Counter(lst_str)
    unique_words = word_freq.keys()
    n_grams = []
    for w in unique_words:
        if '_' in w:
            cur = w
            while '_' in cur:
                next_ = cur[(cur.find('_')+1):]
                if (word_freq[cur] and # greater than 0
                    word_freq[next_] >= minimum and # pass minimum check
                    word_freq[cur] / (word_freq[cur] + word_freq[next_] > threshold) # pass threshold check
                    ): # find n_gram
                    n_grams.append(cur)
                    break
                else:
                    cur = next_
    return set(n_grams) # hashset for fast lookups


def get_result(nouns, known=None):
    """

    :param known:
    :param nouns:
    :return:
    """
    if not known:
        raise ValueError('known cannot be None')
    transformed = []
    for w in nouns:
        if '_' not in w:
            transformed.append(w)
        else:
            cur = w
            added = False
            while '_' in cur:
                if cur in known:
                    transformed.append(cur)
                    added = True
                    break
                cur = cur[(cur.find('_')+1):] # beautiful_painting -> painting
            if not added:
                transformed.append(cur)
    return transformed


def merge_components(sent_components):
    """
    complexity: O(n)
    merge adjacement nouns together
    merge adjacement nouns with one adjative
    :param sent_components:
    :return: merged sent_components
    """
    prev = None
    merged = []
    for w, t in sent_components:
        if prev in NOUN_TYPES and t in NOUN_TYPES:
            last = merged[-1]
            new_word = last[0] + '_' + w
            merged[-1] = (new_word, t)

        elif prev == 'JJ' and t in NOUN_TYPES:
            last = merged[-1]
            new_word = last[0] + '_' + w
            merged[-1] = (new_word, t)

        else:
            merged.append((w, t))
        prev = t
    return merged


if __name__ == '__main__':
    start = time.time()
    # create processing pool
    pool = Pool(cpu_count())

    for i in range(2000, 2017):
        print('processing {}...'.format(i))
        INPUT = json.load(open(DATA_PATH + "/raw/raw_{}.json".format(i)))
        INPUT = [entry.Entry(x).summary for x in INPUT]
        lst_lst_nouns = pool.map(predoc, INPUT)
        lst_nouns = [x for l in lst_lst_nouns for x in l]
        n_grams = find_ngrams(lst_nouns)
        # share n_grams across multiple processes
        target = partial(get_result, known=n_grams)
        result = pool.map(target, lst_lst_nouns)
        json.dump(result, open(DATA_PATH+'/processed/processed_{}.json'.format(i), 'w'))
    pool.close()



