import subprocess
import os
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag
import string
import json
from multiprocessing import Pool, cpu_count

GOOD_TYPES = ['NNS', 'NN', "NNP", 'NNPS', 'JJ']
ALLOWED = set(string.ascii_letters + ' ')
TABLE = str.maketrans(string.punctuation, len(string.punctuation) * " ")


"""
expected format: [string, string, string...]
"""

def preprocess(x):
    output=[]
    for sent in sent_tokenize(x):
        sent = sent.translate(TABLE)
        sent = sent.lower()
        for w, t in pos_tag(word_tokenize(sent)):
            if t in GOOD_TYPES:
                output.append(w)
            else:
                output.append('.')
        output.append('.\n')
    output.append('.')
    return output


def _wordtuple(filename, which, tuple_sz, minimum_count, significance):
    shell_command = "./wordtuples/wordtuples{which} {sz} {mcount} {sig} < {filename}".format(
        which=which,
        sz=tuple_sz,
        mcount=minimum_count,
        sig=significance,
        filename=filename
    )
    result = subprocess.check_output([shell_command], shell=True).decode()
    n_grams = []
    for line in result.split('\n'):
        try:
            sig, *words = line.split(" ")
            n_grams.append((float(sig.strip()), ' '.join(words)))
        except:
            pass

    n_grams = list(filter(lambda t: '.' not in t[1], n_grams))
    return n_grams


def wordtuple(lst_str, sz, minimum_count=5, significance=1e-6,
              which=0, filter_=True, force_new=False):
    tmpfilename = ".{}.wordtuple".format(sum(ord(x) for x in str(lst_str[:1000])) % (2**64-1))
    # if cache file exists, skip preprocessing
    if force_new:
        os.unlink(tmpfilename)

    if not os.path.isfile(tmpfilename):
        pool = Pool(cpu_count())
        lst_lst_word = pool.map(preprocess, lst_str)
        lst_word = []
        for l in lst_lst_word:
            for x in l:
                lst_word.append(x)
            lst_word.append('.\n')
        command_input = ' '.join(lst_word)

        with open(tmpfilename, 'w') as fp:
            fp.write(command_input)

    if which == 0:
        which = ''

    ret = _wordtuple(tmpfilename, which, sz,
                      minimum_count=minimum_count,
                      significance=significance)

    if not filter_:
        return ret
    # filter out ngrams with components of length 1
    return list(filter(lambda x: all(len(y) > 1 for y in x[1].split()), ret))




if __name__ == '__main__':
    lst = json.load(open('text_2014.json'))
    print(wordtuple(lst, 2, which=0))

