from topic_chain import *


tc = TopicChain('topic_keys.json', threshold=0.35, max_incoming=2, max_outgoing=1)


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


def find_root(conns, start):
    """
    :param conns:
    :param start:
    :return: (topic index, level)
    """
    i = 0
    cur = start
    while i < len(conns):
        next_cur = conns[i][cur]
        i += 1
        if not next_cur: # if it is empty, the loop ends
            break

        cur = next_cur[0]
        print(cur)
    return cur, i


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


def in_order(node):
    if node:
        in_order(node.left)
        print(list(reversed(node.key)))
        in_order(node.right)


def squeeze(node):
    if node:
        if not (node.left and node.right):
            if node.left:
                left = node.left
                node.key.extend(left.key)
                node.left = left.left
                if node.left:
                    node.left.parent = node
                node.right = left.right
                if node.right:
                    node.right.parent = node
                squeeze(node)

            elif node.right:
                right = node.right
                node.key.extend(right.key)
                node.right = right.right
                if node.right:
                    node.right.parent = node
                node.left = right.left
                if node.left:
                    node.left.parent = node
                squeeze(node)

        if node.left and node.right:
            squeeze(node.left)
            squeeze(node.right)


if __name__ == '__main__':
    print(len(tc._conn))
    tc.show_conns()
    i,ts = find_root(tc._conn, 0)
    print(i, ts)
    t = tc.get_dynamic_topic(16, 6)
    print(t)

    tree = get_tree(t)
    print(tree)
    squeeze(tree)
    print(tree, end='\n'*3)
    print(depth(tree))
    in_order(tree)










