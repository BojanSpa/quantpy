import ctypes as c
from datetime import datetime

_get_dict = c.pythonapi._PyObject_GetDictPtr
_get_dict.restype = c.POINTER(c.py_object)
_get_dict.argtypes = [c.py_object]

def fromts(ts):
    if len(str(ts)) > 10: ts = ts / 1000
    return datetime.fromtimestamp(ts)

def diff_months(dt1, dt2):
    if (dt1 < dt2): dt1, dt2 = dt2, dt1
    return (dt1.year - dt2.year) * 12 + (dt1.month - dt2.month)

datetime_dict = _get_dict(datetime)[0]
datetime_dict['fromts'] = fromts
datetime_dict['diff_months'] = diff_months