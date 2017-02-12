from topic_chain import *

# this code only works, if the max_incoming is set to 2 and max_outgoing=1, threshold can be adjusted


class Node:
    def __init__(self, key, left=None, right=None, parent=None):
        self.key = key
        self.left=left
        self.right=right
        self.parent=parent

    def _str(self):
        """Internal method for ASCII art. credit to MIT"""
        label = str(self.key)
        if self.left is None:
            left_lines, left_pos, left_width = [], 0, 0
        else:
            left_lines, left_pos, left_width = self.left._str()
        if self.right is None:
            right_lines, right_pos, right_width = [], 0, 0
        else:
            right_lines, right_pos, right_width = self.right._str()
        middle = max(right_pos + left_width - left_pos + 1, len(label), 2)
        pos = left_pos + middle // 2
        width = left_pos + middle + right_width - right_pos
        while len(left_lines) < len(right_lines):
            left_lines.append(' ' * left_width)
        while len(right_lines) < len(left_lines):
            right_lines.append(' ' * right_width)
        if (middle - len(label)) % 2 == 1 and self.parent is not None and \
                        self is self.parent.left and len(label) < middle:
            label += '.'
        label = label.center(middle, '.')
        if label[0] == '.': label = ' ' + label[1:]
        if label[-1] == '.': label = label[:-1] + ' '
        lines = [' ' * left_pos + label + ' ' * (right_width - right_pos), ' ' * left_pos + '/' + ' ' * (middle - 2) +
                 '\\' + ' ' * (right_width - right_pos)] + \
                [left_line + ' ' * (width - left_width - right_width) + right_line
                 for left_line, right_line in zip(left_lines, right_lines)]
        return lines, pos, width

    def __str__(self):
        return '\n'.join(self._str()[0])


def find_root(conns, ts, ti):
    """
    :param conns:
    :param start:
    :return: (topic index, level)
    """
    i = ts
    cur = ti
    while i < len(conns):
        next_cur = conns[i][cur]
        if not next_cur: # if it is empty, the loop ends
            break

        i += 1
        cur = next_cur[0]
    return i, cur


def depth(node):
    if not node: return -1
    return max(depth(node.left), depth(node.right)) + 1


def _get_tree(root, root_topic):
    prevs = root_topic.prev()
    if len(prevs) > 0:
        if len(prevs) > 1:
            right = Node([prevs[1]],parent=root)
            root.right = right
            _get_tree(right, prevs[1])

        left = Node([prevs[0]], parent=root)
        root.left = left
        _get_tree(left, prevs[0])


def get_tree(root_topic):
    root = Node([root_topic])
    _get_tree(root, root_topic)
    return root


def get_size(tree):
    if not tree:
        return 0
    return get_size(tree.left) + get_size(tree.right) + 1


def _in_order(tree, lst):
    if tree:
        _in_order(tree.left, lst)
        lst.append(list(reversed(tree.key)))
        _in_order(tree.right, lst)


def in_order(tree):
    lst = []
    _in_order(tree, lst)
    return lst


def _get_topics(tree, lst):
    if tree:
        topic = tree.key[0]
        t = (topic.ts, topic.ti)
        lst.append(t)
        _get_topics(tree.left, lst)
        _get_topics(tree.right, lst)


def get_topics(tree):
    lst = []
    _get_topics(tree, lst)
    return lst


def get_forest(topic_chain):
    conns = topic_chain.table
    time_len = len(conns)
    index_len = len(conns[0])
    topics_remain = list((i, j) for i in range(time_len+1) for j in range(index_len))
    forest = []
    for i in range(time_len):
        for j in range(index_len):

            # orphan node not connected to any tree
            if not conns[i][j] and (i, j) in topics_remain:
                forest.append(Node([topic_chain.get_dynamic_topic(i,j)]))
                topics_remain.remove((i,j))

            else:
                if (i, j) in topics_remain:
                    ts, ti = find_root(conns, i, j) # find root
                    root_topic = topic_chain.get_dynamic_topic(ts, ti) # find root topic
                    tree = get_tree(root_topic) # construct the tree
                    topics = get_topics(tree) # get all topics from that tree
                    forest.append(tree)
                    for t in topics: # remove all the seen topics from the pool (topics_remain)
                        topics_remain.remove(t)

    return forest


def squeeze(tree):
    if tree:
        if not (tree.left and tree.right):
            if tree.left:
                left = tree.left
                tree.key.extend(left.key)
                tree.left = left.left
                if tree.left:
                    tree.left.parent = tree
                tree.right = left.right
                if tree.right:
                    tree.right.parent = tree
                squeeze(tree)

            elif tree.right:
                right = tree.right
                tree.key.extend(right.key)
                tree.right = right.right
                if tree.right:
                    tree.right.parent = tree
                tree.left = right.left
                if tree.left:
                    tree.left.parent = tree
                squeeze(tree)

        if tree.left and tree.right:
            squeeze(tree.left)
            squeeze(tree.right)

    return tree




def extract(tc, n, verbose=False):
    forest = get_forest(tc)
    top_n = sorted(forest, key=get_size, reverse=True)[:n]
    top_n = [squeeze(x) for x in top_n]
    if verbose:
        for t in top_n:
            print(t)
            print('*' * 200)


    top_n_ordered = [in_order(x) for x in top_n]
    return top_n_ordered


if __name__ == '__main__':
    tc = TopicChain('topic_keys.json', threshold=0.3, max_incoming=2, max_outgoing=1)

    topic_locs = [(16,8), (15,13), (14,24), (13, 6)]
    dts = [tc.get_dynamic_topic(*x) for x in topic_locs]
    print(DynamicTopic.common_words(dts, 10))


    #print(extract(tc, 10, verbose=True))






