import random
def smart_copy(_object):
    """
    recursively copy the built-in containers but no the underlying user objects
    :param _object:
    :return:
    """

    if not isinstance(_object, (list, dict, set, tuple)):
        return _object

    if isinstance(_object, list):
        return [smart_copy(x) for x in _object]

    if isinstance(_object, set):
        return {smart_copy(x) for x in _object}

    if isinstance(_object, tuple):
        return tuple(smart_copy(x) for x in _object)

    if isinstance(_object, dict):
        return {x: smart_copy(_object[x]) for x in _object}


def get_class(t):
    s = str(type(t))
    return s[s.find("'")+1: s.rfind("'")]


def guess_type(_object):
    # assume uniformity
    if isinstance(_object, list):
        t = guess_type(_object[0])
        for x in _object:
            if guess_type(x) != t:
                raise ValueError('inconsistency found')
        return get_class(_object)+"("+guess_type(_object[0])+")"

    if isinstance(_object, tuple):
        return get_class(_object)+'('+', '.join(guess_type(x) for x in _object)+')'

    if isinstance(_object, set):
        it = iter(_object)
        val = next(it)
        t = guess_type(val)
        for x in _object:
            if guess_type(x) != t:
                raise ValueError('inconsistency found')
        return get_class(_object)+"("+guess_type(val)+")"

    if isinstance(_object, dict):
        it = iter(_object.items())
        key, val = next(it)
        key_t = guess_type(key)
        val_t = guess_type(val)
        for x in _object:
            if guess_type(x) != key_t:
                raise ValueError('inconsistency found')
            if guess_type(_object[x]) != val_t:
                raise ValueError('inconsistency found')
        return get_class(_object)+"("+guess_type(key)+" : "+guess_type(val)+")"

    return get_class(_object)




if __name__ == '__main__':
    a = [('a', {1,}, {(1,"s"):2})] * 100000
    b = smart_copy(a)
    print(guess_type(a))