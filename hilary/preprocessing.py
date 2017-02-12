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
from nltk.tokenize import RegexpTokenizer, sent_tokenize, word_tokenize
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer


# Constants
NOUN_TYPES = ('NN','NNS','NNP','NNPS')
PLURAL_NOUN_TYPES = ('NNS', 'NNPS')
DATA_PATH = '/Users/ranxiao/Desktop/data/arXiv'
REMOVED = ['www', 'http', 'com']


# Acquired resources
lemmatizer = WordNetLemmatizer()
word_tokenizer = RegexpTokenizer(r'[a-zA-Z\']+')


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
        # lemmatization # don't convert text to lowercase if the lemmatization, as the case can give
        # lemmatizater context and perform more accurately. ("Sessions" -> "Sessions" and "sessions" -> "session")
        sent_components = [(lemmatizer.lemmatize(w), t) if t in PLURAL_NOUN_TYPES else (w, t) for (w, t) in sent_components]
        # merge
        sent_components = merge_components(sent_components)
        # get only nouns
        nouns = [w for w, t in sent_components if t in NOUN_TYPES]
        result.extend(nouns)
    # get lower
    return [x.lower() for x in result]


def find_ngrams(lst_str, threshold=0.2, minimum=10):
    """
    discover n-grams from the corpus
    :param lst_str: nouns
    :param threshold:  ex occur(congressional_meeting) / occur(meeting) > threshold
    :param minimum: minimum number of occurences in the corpus
    :return:  a list of n-grams
    """
    word_freq = Counter(lst_str)
    unique_words = word_freq.keys()
    n_grams = []
    for w in unique_words:
        if '_' in w:
            cur = w
            while '_' in cur:
                next_ = cur[(cur.find('_')+1):]
                if (word_freq[cur] and # greater than 0
                    # n_gram appear greater than n times  and (n-1)_gram appear greater than n times
                    # different heuristics can be tried here to improve n-grams capture
                    (word_freq[next_] >= minimum and word_freq[cur] >= minimum) and # pass minimum check
                    word_freq[cur] / (word_freq[cur] + word_freq[next_] >= threshold) # pass threshold check
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
    if known is None:
        raise ValueError('known cannot be none')
    if not known:
        raise ValueError('known cannot be emtpy!')

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


def prepredoc(text):
    lst = text.split()
    new_lst = []
    for x in lst:
        remove=False
        for c in '=:/-@':
            if c in x:
                remove=True
                break

        for w in REMOVED:
            if w in x.lower():
                remove=True
                break

        if not remove:
            new_lst.append(x)
    return ' '.join(new_lst)


if __name__ == '__main__':
    start = time.time()
    # create processing pool
    pool = Pool(cpu_count())

    for i in range(2009, 2012):
        for j in range(4):
            print('processing {}...'.format((i,j)))
            raw = json.load(open('{}:{}.json'.format(i, j)))
            wrangled = pool.map(prepredoc, raw)
            lst_lst_nouns = pool.map(predoc, wrangled)
            lst_nouns = [x for l in lst_lst_nouns for x in l]
            n_grams = find_ngrams(lst_nouns)
            print(n_grams)
            # share n_grams across multiple processes (it's OK because it is read only)
            target = partial(get_result, known=n_grams)
            result = pool.map(target, lst_lst_nouns)
            json.dump(result, open('processed_{}_{}.json'.format(i,j), 'w'))
    pool.close()



