from gensim.models.wrappers.ldamallet import LdaMallet
import json


DATA_PATH = '../data/hilary'
result = []
for i, m in (i, m for i in range(3) for m in range(4)):
        topic_keys = []
        model_path = DATA_PATH+'/mallet_files/hilary_{}_{}_mallet_model'.format(2009+i, m)
        lda = LdaMallet.load(model_path)
        for i in range(30): # num of topics
            topic_keys.append({w:str(p) for w, p in lda.show_topic(i, num_words=100)})
        result.append(topic_keys)

json.dump(result, open('topic_keys.json', 'w'))


