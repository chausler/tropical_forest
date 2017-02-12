import json
from collections import Counter
DATA_PATH = '../data/arXiv'


inference_result = json.load(open('topic_inference.json'))
top_words = []
for i in range(17): # period
    lst = json.load(open(DATA_PATH + '/processed/processed_{}.json'.format(i+2000)))
    inference_result_at = inference_result[i]
    top_words_at = []
    for j in range(30): # num_topics
        word_doc_freq = Counter()
        relevant_docs = [lst[i] for i, t in enumerate(inference_result_at) if t == j]
        all_words = [w for doc in relevant_docs for w in doc]
        word_freq = Counter(all_words)
        for doc in relevant_docs:
            unique_words = set(doc)
            word_doc_freq.update(unique_words)
        word_lift = {}
        for w in word_freq:
            word_lift[w] = 0
            if word_doc_freq[w] >= 0.2 * len(relevant_docs):
                word_lift[w] = word_freq[w] / word_doc_freq[w]

        top30 = [x[0] for x in sorted(word_lift.items(), key=lambda x:x[1])][:30]
        top_words_at.append(top30)
    print(top_words_at)
    top_words.append(top_words_at)
json.dump(top_words, open('topic_keys_lift.json', 'w'))








