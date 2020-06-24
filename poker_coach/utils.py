""" Helper functions. """


from typing import Iterator


def flatten(i: Iterator) -> Iterator:
    """ Flatten an irregular iterable. """
    for i in i:
        if isinstance(i, Iterator):
            yield from i
        else:
            yield i
