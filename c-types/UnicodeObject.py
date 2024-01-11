#!/usr/bin/env python3.10

import ctypes

assert ctypes.cast(id(42), ctypes.py_object).value == 42

# [unicodeobject.h](https://github.com/python/cpython/blob/3.10/Include/cpython/unicodeobject.h#L85-L244)
# [unicodeobject.c](https://github.com/python/cpython/blob/3.10/Objects/unicodeobject.c)
# [PyObject](https://github.com/python/cpython//blob/3.10/Include/object.h#L105-L109)

class PyObject(ctypes.Structure):
    _fields_ = [
        ("ob_refcnt", ctypes.c_long),
        ("ob_type", ctypes.c_void_p),
    ]
    
class PyASCIIObject(PyObject):
    # internal fields of the string object
    _fields_ = [
        ("length", ctypes.c_ssize_t),
        ("hash", ctypes.c_ssize_t),
        ("interned", ctypes.c_uint, 2),
        ("kind", ctypes.c_uint, 3),
        ("compact", ctypes.c_uint, 1),
        ("ascii", ctypes.c_uint, 1),
        ("ready", ctypes.c_uint, 1),
        ("_padding", ctypes.c_uint, 24),
        ("wstr", ctypes.POINTER(ctypes.c_wchar))
    ]

    def __repr__(self) -> str:
        return f"ob_refcnt[{self.ob_refcnt}], length[{self.length}], interned[{self.interned}], kind[{self.kind}], compact[{self.compact}], ascii[{self.ascii}], ready[{self.ready}]"
    
class PyCompactUnicodeObject(PyASCIIObject):
    # internal fields of the string object
    _fields_ = [
        ("utf8_length", ctypes.c_ssize_t),
        ("utf8", ctypes.POINTER(ctypes.c_char)),
        ("wstr_length", ctypes.c_ssize_t),
    ]

    def __repr__(self) -> str:
        return super().__repr__() + f" utf8_length[{self.utf8_length}], utf8[{self.utf8}], wstr_length[{self.wstr_length}]"
    
class PyUnicodeObject(PyCompactUnicodeObject):
    class _Data(ctypes.Union):
        _fields_ = [
            ("any", ctypes.c_void_p),
            ("latin1", ctypes.POINTER(ctypes.c_uint8)),
            ("ucs2", ctypes.POINTER(ctypes.c_uint16)),
            ("ucs4", ctypes.POINTER(ctypes.c_uint32)),
        ]
    
    _fields_ = [
        ("data", _Data),
    ]
    
print(ctypes.sizeof(PyASCIIObject))

# assert PyUnicodeObject.from_address(id("Hello")).kind == 1
# assert PyUnicodeObject.from_address(id("你好")).kind == 2
# assert PyUnicodeObject.from_address(id("🤨")).kind == 4

# keep it from GC
# 1. compact ascii: kind[1], compact[1], ascii[1], ready[1]
print(f"\n -compact ascii:")
string_obj = "Hello, ctypes!"
addr = id(string_obj)
ascii_obj = PyASCIIObject.from_address(addr)
print(ascii_obj)

# compact ascii: data starts just after the structure
data_addr = addr + ctypes.sizeof(PyASCIIObject)
data = ctypes.cast(data_addr, ctypes.c_char_p)
print(f"data: {data.value}")


# 2. compact: kind[2], compact[1], ascii[0], ready[1]
print(f"\n -compact:")
string_obj = "你好!"
addr = id(string_obj)
ascii_obj = PyASCIIObject.from_address(addr)
print(ascii_obj)

compact_obj = PyCompactUnicodeObject.from_address(addr)
print(compact_obj)

# compact: data starts just after the structure
data_addr = addr + ctypes.sizeof(PyCompactUnicodeObject)
data = ctypes.cast(data_addr, ctypes.POINTER(ctypes.c_uint16))
print(f"data: {data[0]}, {data[0]:#06x}, {chr(data[0])}")
print(f"data: {data[1]}, {data[1]:#06x}, {chr(data[1])}")
print(f"data: {data[2]}, {data[2]:#06x}, {chr(data[2])}")
print(f"NULL: {data[3]}, {data[3]:#06x}, {chr(data[3])}")


# 3. compact: kind[4], compact[1], ascii[0], ready[1]
print(f"\n -compact:")
string_obj = "你好🤨"
addr = id(string_obj)
ascii_obj = PyASCIIObject.from_address(addr)
print(ascii_obj)

compact_obj = PyCompactUnicodeObject.from_address(addr)
print(compact_obj)

# compact: data starts just after the structure
data_addr = addr + ctypes.sizeof(PyCompactUnicodeObject)
data = ctypes.cast(data_addr, ctypes.POINTER(ctypes.c_uint32))
print(f"data: {data[0]}, {data[0]:#010x}, {chr(data[0])}")
print(f"data: {data[1]}, {data[1]:#010x}, {chr(data[1])}")
print(f"data: {data[2]}, {data[2]:#010x}, {chr(data[2])}")
print(f"NULL: {data[3]}, {data[3]:#010x}, {chr(data[3])}")

# 4. legacy string: kind[2], compact[0], ascii[0] is deprecated
# I can't produce it in Python3.10, maybe you can try python2.7