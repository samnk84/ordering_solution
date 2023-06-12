class AnyOrder(list):
    def __init__(self, iterable, key=None):
        super().__init__(iterable)
        self._key = key

    def __eq__(self, other):
        return sorted(self, key=self._key) == sorted(other, key=self._key)


class Any:
    def __init__(self, _type):
        self._type = _type

    def __repr__(self):
        return f"Any({self._type.__name__})"

    def __eq__(self, other):
        return isinstance(other, self._type)
