# typing.py
# Minimal fake typing module for MicroPython.
# Lets you write type hints like List, Dict, Tuple, Optional, Any, etc.

class _Type:
    def __getitem__(self, item):
        return self

    def __call__(self, *args, **kwargs):
        return self

Any = _Type()
Union = _Type()
Optional = _Type()
List = _Type()
Dict = _Type()
Tuple = _Type()
Set = _Type()
FrozenSet = _Type()
Callable = _Type()
Iterable = _Type()
Iterator = _Type()
Sequence = _Type()
Mapping = _Type()
Type = _Type()
Literal = _Type()
Final = _Type()
ClassVar = _Type()


def cast(type_hint, value):
    return value


def get_type_hints(obj):
    return getattr(obj, "__annotations__", {})


def overload(func):
    return func


def final(obj):
    return obj


def runtime_checkable(cls):
    return cls


class Protocol:
    pass


class Generic:
    pass


class TypeVar:
    def __init__(self, name, *constraints, **kwargs):
        self.name = name
        self.constraints = constraints
        self.kwargs = kwargs


class NamedTuple(tuple):
    pass