def compat_bytes(item, encoding=None):
    """
    This method is required because Python 2.7 `bytes` is simply an alias for `str`. Without this method,
    code execution would look something like:
    class clazz(object):
        def __bytes__(self):
            return bytes(5)
    Python 2.7:
    c = clazz()
    bytes(c)
    >>'<__main__.clazz object at 0x105171a90>'
    In this example, when `bytes(c)` is invoked, the interpreter then calls `str(c)`, and prints the above string.
    the method `__bytes__` is never invoked.
    Python 3.6:
    c = clazz()
    bytes(c)
    >>b'\x00\x00\x00\x00\x00'
    This is the expected and necessary behavior across both platforms.
    w/ compat_bytes method, we will ensure that the correct bytes method is always invoked, avoiding the `str` alias in
    2.7.
    :param item: this is the object who's bytes method needs to be invoked
    :param encoding: optional encoding parameter to handle the Python 3.6 two argument 'bytes' method.
    :return: a bytes object that functions the same across 3.6 and 2.7
    """
    if hasattr(item, '__bytes__'):
        return item.__bytes__()
    else:
        if encoding:
            return bytes(item, encoding)
        else:
            return bytes(item)
