from gensim.matutils import hellinger
import json

# define a merge
# when more than 1 topic_dist points to a particular topic_dist in the next time slice.


# define a split
# a particular topic_dist points to more than 1 topic_dist in the next time slice.
class DynamicTopic:
    """
    
    """
    def __init__(self, dynamic_model, time_slice, topic_n):
        self._dm = dynamic_model
        self._time_slice = time_slice
        self._topic_n = topic_n

    def next(self):
        next_time_slice = self._time_slice + 1
        if next_time_slice >= len(self._dm._conn):
            return []
        related_future_topic_indexes = self._dm.get_outgoing_connections(self._time_slice, self._topic_n)
        return [DynamicTopic(self._dm, next_time_slice, i) for i in related_future_topic_indexes]

    def prev(self):
        prev_time_slice = self._time_slice-1
        if prev_time_slice < 0: return []
        related_previous_topic_indexes = [i for i, t in enumerate(self._dm._conn[prev_time_slice]) if self._topic_n in t]
        return [DynamicTopic(self._dm, prev_time_slice, i) for i in related_previous_topic_indexes]

    def __str__(self):
        # printout = str(self._dm.get_topic_keys(self._time_slice, self._topic_n))
        # if len(printout) > 200:
        #     return printout[:200]+'...'
        # return printout
        return str((self._time_slice, self._topic_n))

    __repr__ = __str__


class TopicChain:
    """
    json format [[{topic(k:p)}, {topic}, {topic} ...]... more time_slices... ] == list(list(dict)))
    while k is the keyword and p is the probability
    """
    def __init__(self, json_, **kwargs):
        self._data = json.load(open(json_))
        self._data = [[{k: float(y[k]) for k in y} for y in x] for x in self._data]

        self._threshold = kwargs.get('threshold') or 0.35
        self._max_outgoing = kwargs.get('max_outgoing') or 1
        self._max_incoming = kwargs.get('max_incoming') or 2
        self._nkeys = kwargs.get('nkeys') or 20
        self._conn = self._generate_conns_from_data()

    @property
    def nkeys(self):
        return self._nkeys

    @nkeys.setter
    def nkeys(self, new_value):
        self._nkeys = new_value
        self._conn = self._generate_conns_from_data()

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, new_value):
        self._threshold = new_value
        self._conn = self._generate_conns_from_data()

    @property
    def max_outgoing(self):
        return self._max_outgoing

    @max_outgoing.setter
    def max_outgoing(self, new_value):
        self._max_outgoing = new_value
        self._conn = self._generate_conns_from_data()

    @property
    def max_incoming(self):
        return self._max_incoming

    @max_incoming.setter
    def max_incoming(self, new_value):
        self._max_incoming = new_value
        self._conn = self._generate_conns_from_data()

    def get_topics_with_outgoing_connections(self, time_slice):
        return [i for i, x in enumerate(self._conn[time_slice]) if len(x)]

    def get_outgoing_connections(self, time_slice, topic_n):
        return self._conn[time_slice][topic_n]

    def get_topic_keys(self, time_slice, topic_n):
        return self._data[time_slice][topic_n]

    def get_dynamic_topic(self, time_slice, topic_n):
        return DynamicTopic(self, time_slice, topic_n)

    def _generate_conns_from_data(self):
        result = []
        data = self._data
        for i in range(len(data) - 1):
            lda_topic_1 = data[i]
            lda_topic_2 = data[i+1]
            lda_topic_1 = [sorted([(topic[k], k) for k in topic], key=lambda x: -x[0]) for topic in lda_topic_1]
            lda_topic_2 = [sorted([(topic[k], k) for k in topic], key=lambda x: -x[0]) for topic in lda_topic_2]
            l = len(lda_topic_1)
            d_matrix = [[None] * l for _ in range(l)]
            for i in range(l):
                for j in range(l):
                    d_matrix[i][j] = self.compute_hellinger(lda_topic_1[i][:self._nkeys], lda_topic_2[j][:self._nkeys])
            slice_result = []
            for group in self.get_edges_between_two_time_slices(d_matrix,
                                                                self.threshold,
                                                                self.max_outgoing,
                                                                self.max_incoming):
                
                slice_result.append(group)
            result.append(slice_result)
        return result

    def show_conns(self):
        for i, slice in enumerate(self._conn):
            line = '{}:'.format(i) + str(''.join(['{}:{}| '.format(i, t) for i, t in enumerate(slice)]))
            print(line)
            print(len(line) * '-')


    # def get_conns(self):
    #     return


    @staticmethod
    def compute_hellinger(dist01, dist02):
        unique_words = set([x[1] for x in dist01] + [x[1] for x in dist02])
        dict_dist01 = {x[1]: x[0] for x in dist01}
        dict_dist02 = {x[1]: x[0] for x in dist02}
        vec01 = [dict_dist01.get(x, 0) for x in unique_words]
        vec02 = [dict_dist02.get(x, 0) for x in unique_words]
        return hellinger(vec01, vec02)

    @staticmethod
    def get_edges_between_two_time_slices(distance_table, threshold, max_outgoing, max_incoming):
        lst = []
        l = len(distance_table)
        # find outgoing connections under the limit
        for i in range(l):
            outgoings = list(filter(lambda x: distance_table[i][x] < threshold, range(l)))
            if len(outgoings) > max_outgoing:
                outgoings = sorted(outgoings, key=lambda x: distance_table[i][x])[:max_outgoing]
            lst.append(outgoings)

        # restrict the number of incoming connections from the 'merge'
        for j in range(l):
            incoming_conns = [i for i, p in enumerate(lst) if j in p]
            if len(incoming_conns) > max_incoming:
                conns_removed =sorted(incoming_conns, key=lambda x: distance_table[x][j])[max_incoming:]
                for i in conns_removed:
                    lst[i].remove(j)
        return lst

if __name__ == '__main__':
    dm = TopicChain('topic_keys.json',
                    threshold=0.35,
                    max_incoming=2,
                    max_outgoing=1
                    )

    for slice in dm._conn:
        print(slice)
    # print(dm.get_topics_with_outgoing_connections(0))
    # print(dm.get_outgoing_connections(0, 2))
    # print(dm.get_topic_keys(0, 14))
    # print(dm.get_topic_keys(1, 0))
    # print(dm._conn)
    # dm.threshold = 0.4
    # print("*" * 200)
    # print(dm._conn)
    # print(dm.get_dynamic_topic(0,0))
    # print(dm.get_dynamic_topic(0,0).next())
    # dm.max_outgoing = 1
    # print(dm._conn)
