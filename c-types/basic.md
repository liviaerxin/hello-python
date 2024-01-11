
`string -> memory address -> string`

```py
>>> string_obj = b"hello"
# construct from a string
>>> c_obj = ctypes.c_char_p(string_obj)
>>> c_obj
c_char_p(140075714085328)
# get the pointer value which is a address pointing to the string
>>> ctypes.cast(c_obj, ctypes.c_void_p).value
140075714085328
# !!! pointer address
>>> ctypes.addressof(c_obj)
140075714740112
# construct from memory address
>>> ctypes.c_char_p(140075714085328)
c_char_p(140075714085328)
>>> ctypes.c_char_p(140075714085328).value
b'hello'
>>>
```

`pointer`

```py
>>> string_obj = b"hello"
>>> ctypes.c_char_p(string_obj)
c_char_p(140397565009920)
>>> char_p = ctypes.cast(140397565009920, ctypes.POINTER(ctypes.c_char))
>>> char_p[0]
b'h'
>>> char_p[1]
b'e'
>>> char_p[2]
b'l'
>>> char_p[3]
b'l'
>>> char_p[4]
b'o'
# NULL terminated
>>> char_p[5]
b'\x00'
```

