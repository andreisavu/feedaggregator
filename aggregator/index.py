
import logging as log

from time import time

def add_padding(value, length=15, ch='0'):
    """
    Preppend the value with the padding char until it reaches the length

    >>> add_padding('1', 5)
    '00001'

    >>> add_padding('12345', 2)
    '12345'

    """
    value = str(value)
    l = len(value)
    if l < length:
        return "%s%s" % (ch * (length - l), value)
    return value

def build_key(cat, timestamp, feed=None, client=None, collision_check=False):
    """
    Build an index key based on category and timestamp

    If there is a collision simply append an increment counter

    >>> build_key('cat', 1)
    'cat/000000000000001'

    """
    key = '%s/%s' % (cat, add_padding(int(timestamp)))
    if collision_check:
        new_key, index = key, 1
        while True:
            res = client.getRow('UrlsIndex', new_key)
            if not res: break

            if res[0].columns['Url:'].value == feed:
                return new_key
            new_key = "%s+%s" % (key, add_padding(index, 3))
            index += 1
 
        return new_key
    return key

if __name__ == '__main__':
    import doctest
    doctest.testmod()

