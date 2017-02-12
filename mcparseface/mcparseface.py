import json
import os
import string
import subprocess

from nltk.tokenize import sent_tokenize

ORIGINAL_DIR = os.getcwd()
MCPARSEFACE_DIR = '/Users/ranxiao/Desktop/google/models/syntaxnet'
WORD = 1
WORDTYPE = 4
ALLOWED = string.ascii_letters + '.,?! '
DUMMY = '654321'
TEMP_FILE_NAME = 'parseface_tmpface.tmp'
FIRST = 0

def is_dummy(sent):
    return len(sent) == 1 and sent[FIRST][0] == DUMMY


def insert_dummies(lst_document):
    lst_sent = []
    for document in lst_document:
        for sent in sent_tokenize(document):
            sent = ''.join([x for x in sent if x in ALLOWED])
            lst_sent.append(sent)

        # used as boundary to isolate each documents
        lst_sent.append(DUMMY)

    return lst_sent


def sents2docs(sents):
    i, l = 0, len(sents)
    result = []
    temp = []
    while i < l:
        sent = sents[i]
        if not is_dummy(sent):
            temp.extend(sent)
        else:
            result.append(temp)
            temp = []
        i += 1
    return result


def tbl2tuples(text):
    result = []
    lines = text.split('\n')
    for line in lines:
        items = line.split('\t')
        try:
            w, t = items[WORD], items[WORDTYPE] # raise Exception
            # remove punctuations
            w = w[:-1] if not w[-1].isalnum() and len(w) > 1 else w
            result.append((w, t))
        except IndexError:
            # avoid check items on every iteration
            pass
    return result


def pos_tag(text, verbose=False):
    """
    :param text: accept a single str or a python list of strs or strs with '\n' as separator
    :optional param verbose: if True, will output extra printout from
    :return: [(word, word_type)...] or [[(word, word_type)...],...]
    """
    single = True
    if '\n' in text:
        text = text.split('\n')
        single=False

    if isinstance(text, list):
        # replace '\n' with ' ' in the each string
        text = [t.replace('\n', ' ') for t in text]
        # put dummy between sents of separate documents so later the sents can be separated
        lst_sent = insert_dummies(text)
        text = '\n'.join(lst_sent)
        single = False

    # you have to navigate to this directory, otherwise the syntaxnet/myparser.sh will not work
    os.chdir(MCPARSEFACE_DIR)
    # remove the tmp if it already exists
    if os.path.isfile(TEMP_FILE_NAME):
        os.unlink(TEMP_FILE_NAME)

    # the primary reason to use a temp is when using echo, the command can get too long and raise  OSError, so saving
    # a tempfile is a roundabout way to avoid that.
    with open(TEMP_FILE_NAME, 'w') as tmpfile:
        tmpfile.write(text)

    # command = """cat .temp.txt | syntaxnet/myparser.sh | grep -E '^[1-9]+\t'""" % (text)
    command = """printf '%b\n' "$(cat {})" | syntaxnet/myparser.sh""".format(TEMP_FILE_NAME)
    stderr = None
    if not verbose:
        stderr = open(os.devnull, 'w')
    command_result = subprocess.check_output([command], stderr=stderr, shell=True)
    os.chdir(ORIGINAL_DIR)

    command_result = command_result.decode()
    # print(result) # debug only
    chunks = []
    i, j = 0, 0
    while 1:
        j = command_result.find('\n1\t', i+1)
        if j != -1:
            chunks.append(command_result[i:j])
        else:
            break
        i = j

    if i < len(command_result):
        chunks.append(command_result[i:])

    sents = [tbl2tuples(x) for x in chunks]
    if single:
        return sents[0]

    # merge sents into documents
    return sents2docs(sents)

if __name__ == '__main__':
    lst_document = json.load(open('emails.json'))
    for d in pos_tag(lst_document, verbose=True):
        print(d)
