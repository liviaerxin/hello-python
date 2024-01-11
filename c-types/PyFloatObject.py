#!/usr/bin/env python3.10

import ctypes
import sys

# [floatobject.h](https://github.com/python/cpython/blob/main/Include/cpython/floatobject.h#L8)
# [PyObject](https://github.com/python/cpython//blob/3.10/Include/object.h#L105-L109)
# [ctypes](https://docs.python.org/3/library/ctypes.html)
class PyObject(ctypes.Structure):
    _fields_ = [
        ("ob_refcnt", ctypes.c_long),  # 8 bytes
        ("ob_type", ctypes.c_void_p),  # 8 bytes in 64 bit
    ]

class PyFloatObject(PyObject):
    _fields_ = [
        ("ob_fval", ctypes.c_double), # 8 bytes in 64 bit
    ]

    def __repr__(self) -> str:
        return f"ob_refcnt[{self.ob_refcnt}], ob_type[{self.ob_type}], ob_fval[{self.ob_fval}]"


print(ctypes.sizeof(PyFloatObject))

float_obj = 32.123
print(f"sizeof bytes_obj: {sys.getsizeof(float_obj)}")

addr = id(float_obj)

# Get ctypes object from memory address which points to C data structure
py_bytes_obj = PyFloatObject.from_address(addr)
print(py_bytes_obj)
