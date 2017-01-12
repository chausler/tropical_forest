"""
Assume input is a lst of strings
"""
from nltk.tokenize import RegexpTokenizer, sent_tokenize
# from nltk.tag.stanford import StanfordPOSTagger
from nltk import pos_tag
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
import json



NOUN_TYPES = ('NN','NNS','NNP','NNPS')
word_tokenizer = RegexpTokenizer(r'[a-z]+')
# pos_tagger = StanfordPOSTagger(path_to_jar='/usr/local/Cellar/stanford-postagger-full-2015-12-09/stanford-postagger.jar',
#                                model_filename='/usr/local/Cellar/stanford-postagger-full-2015-12-09/models/english-bidirectional-distsim.tagger'
#                                )


def preprocess_document(text):
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
        # sent_components = pos_tagger.tag(words) # doesn't run well, as the pos_tagger is just a wrapper of java cli
        sent_components = merge_components(sent_components)
        for w, t in sent_components:
            if t in NOUN_TYPES:
                result.append(w)
    # filter out random characters
    result = [test_ngrams(text, x) for x in result]
    return [w for w in result if len(w) > 2]


def test_ngrams(text, phrase, threshold=0.1, minimium_count=2):
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
        phrase_count = text.count(phrase)
        sub_phrase = ' '.join(components[i:])
        sub_phrase_count = text.count(sub_phrase)
        if (phrase_count > minimium_count) and (phrase_count / sub_phrase_count >= threshold) and (len(components[i-1]) > 1):
            break
        phrase = sub_phrase
        i += 1
    return phrase.replace(' ', '_')


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
    # create processing pool
    pool = Pool(cpu_count())
    # get input
    print('get input...')

    # json format ['plain text',........]
    INPUT = json.load(open('json_files/enron_full.json'))
    # processing
    print('processing...')
    lst = pool.map(preprocess_document, INPUT)
    print('dump processed data to json...')
    json.dump(lst, open('json_files/enron2.json', 'w'))


