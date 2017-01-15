"""
Assume input is a lst of strings
"""
__author__ = 'Ran Xiao'

import time
from nltk.tokenize import RegexpTokenizer, sent_tokenize
from nltk import pos_tag
from multiprocessing import Pool, Lock
from multiprocessing import cpu_count, Manager
import json
from functools import partial

NOUN_TYPES = ('NN','NNS','NNP','NNPS')
word_tokenizer = RegexpTokenizer(r'[a-z]+')
individual_cache = {}


def _preprocess_document(text, cache=None):
    """
    turn text into a list of tokens aka list of string for lda
    :param text:
    :return:
    """
    result = []
    # convert upper case to lower case
    text = text.lower()
    for sent in sent_tokenize(text):
        # tokenize words
        words = [word for word in word_tokenizer.tokenize(sent)]
        # get sent components
        sent_components = pos_tag(words)
        # sent_components = pos_tagger.tag(words) # doesn't run well, as the pos_tagger is just a wrapper of java cli.
        sent_components = merge_components(sent_components)
        for w, t in sent_components:
            if t in NOUN_TYPES:
                result.append(w)
    # filter out random characters
    result = [test_ngrams(text, x, cache) for x in result]
    ret = [w for w in result if len(w) > 2]
    # print(ret) # for debugging
    return ret


# install a cache
preprocess_document = partial(_preprocess_document, cache=individual_cache)


def test_ngrams(text, phrase, cache=None, threshold=0.1, minimium_count=2):
    """
    simple function to test to see whehter a given ngram should be included.
    if a collocation is worthy to be included, return the collocation, otherwise return second part of the collocation
    for example, white house, if it appears at least greater than or equal to the minimum count in the document, and
    frequency of white house over frequency of house is over the threshold in the entire document, return white house,
    otherwise, return house.
    :param text: str
    :param phrase: ex white_house
    :return: white_house or house depend on the situation
    """

    phrase = phrase.replace('_', ' ')
    components = phrase.split()
    if len(components) == 1:
        return phrase
    i=1
    while i < len(components):

        # check to see if the phrase has been identified
        if cache and '_'.join(components[i-1:]) in cache:
            return '_'.join(components[i-1:])

        phrase_count = text.count(phrase)
        sub_phrase = ' '.join(components[i:])
        sub_phrase_count = text.count(sub_phrase)
        if phrase_count > minimium_count and phrase_count / sub_phrase_count >= threshold:
            break
        phrase = sub_phrase
        i += 1
    ret = phrase.replace(' ', '_')
    if cache:
        cache[ret] = None
    return ret


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
    # get input
    print('get input...')

    for i in range(2000, 2017):
        INPUT = json.load(open("raw_{}.json".format(i)))
        print('processing {}...'.format(i))
        lst = pool.map(preprocess_document, INPUT)
        print('dump processed data to json...')
        json.dump(lst, open('processed_{}.json'.format(i), 'w'))
        print('finished after {}s'.format(time.time()-start))


