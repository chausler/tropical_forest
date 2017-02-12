from itertools import chain
from collections import Counter
from topic_chain import *

TAB = ' '*4


class ConnectedComponents:
    def __init__(self, tc):
        """
        initializer
        :param tc:  TopicChain object
        """
        self._ts, self._ti = tc.shape
        self._marked = [[False] * self._ti for _ in range(self._ts)]
        self._id = [[-1] * self._ti for _ in range(self._ts)] # -1 is just a placeholder
        self._tc = tc
        self.run()
        self._n = None

    def _adj(self, ts, ti):
        """
        get the adjacent topics
        :param ts: time slice
        :param ti: topic id
        :return: iterable of (topic.ts, topic.id)
        """
        dt = self._tc.get_dynamic_topic(ts, ti)
        for dt in (dt.next() + dt.prev()):
            yield dt.ts, dt.ti

    def _next(self, ts, ti):
        """
        get the connected topics in the next slice
        :param ts: time slice
        :param ti: topic id
        :return: iterable of (topic.ts, topic.id)
        """
        dt = self._tc.get_dynamic_topic(ts, ti)
        for dt in dt.next():
            yield dt.ts, dt.ti

    def _dfs(self, ts, ti, id_):
        """
        dfs
        :param ts: time slice
        :param ti: topic id
        :param id_: connected component id
        :return: None
        """
        self._marked[ts][ti] = True
        self._id[ts][ti] = id_
        for i, j in self._adj(ts, ti):
            if not self._marked[i][j]:
                self._dfs(i, j, id_)

    def run(self):
        """
        use dfs to find groups of connected components
        :return: None
        """
        id_ = 0
        for i in range(self._ts):
            for j in range(self._ti):
                if not self._marked[i][j]:
                    self._dfs(i, j, id_)
                    id_ += 1

    def __len__(self):
        """
        return the total number of the connected components
        :return:
        """
        if not self._n:
            self._n = max(x for y in self._id for x in y) + 1
        return self._n

    def get_group_with(self, id_):
        group = []
        for i in range(self._ts):
            for j in range(self._ti):
                if self._id[i][j] == id_:
                    group.append((i,j))
        return group

    def get_largest(self, n):
        """
        get the dot file of n largest connected components
        :param n: n of connected components
        :return: string form of the .dot file
        """
        counter = Counter(chain(*self._id))
        ids = [i for i, _ in counter.most_common()[:n]]
        return self.get_dot_with(ids)

    def get_dot_with(self, ids, nwords=8):
        """
        get the dot file of selected connected components
        :param ids: list of connected components ids
        :param nwords: top n keywords
        :return: string form of the .dot file
        """
        edges = []
        for id_ in ids:
            edges.append(self.get_group_with(id_))
        chained = chain(*edges)
        strs = []
        for ts, ti in chained:
            tws_1 = ', '.join(self._tc.get_dynamic_topic(ts, ti).top_words[:nwords])
            for nts, nti in self._next(ts, ti):
                tws_2 = ', '.join(self._tc.get_dynamic_topic(nts, nti).top_words[:nwords])
                strs.append('\"({},{}):{}\" -> \"({},{}):{}\";'.format(ts, ti, tws_1, nts, nti, tws_2))
        return "digraph unix {\n"+TAB+"size=\"6,6\";\n"+TAB+'\n{}'.format(TAB).join(strs)+ "\n}"


if __name__ == '__main__':
    tc = TopicChain('topic_keys.json', max_incoming=2, max_outgoing=2, threshold=0.35)
    cc = ConnectedComponents(tc)
    print(len(cc))
    print(cc.get_largest(6))