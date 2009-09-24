
def smart_str(s, encoding='utf-8', errors='replace'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.
    """
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

def any_in(needles, haystack):
    for x in needles:
        if x in haystack: return True
    return False

def split_csv(cats):
    return filter(None, [x.strip() for x in cats.split(',')])

