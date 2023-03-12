import ctypes as c
from datetime import datetime

_get_dict = c.pythonapi._PyObject_GetDictPtr
_get_dict.restype = c.POINTER(c.py_object)
_get_dict.argtypes = [c.py_object]

def fromts(ts):
    if len(str(ts)) > 10: ts = ts / 1000
    return datetime.fromtimestamp(ts)

datetime_dict = _get_dict(datetime)[0]
datetime_dict['fromts'] = fromts