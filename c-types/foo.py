import ctypes


class Foo(ctypes.Structure):
    _fields_ = [
        ("a", ctypes.c_int),
        ("b", ctypes.c_double),
        ("c", ctypes.c_long),
    ]

    def __repr__(self) -> str:
        return f"Foo(a={self.a}, b={self.b}, c={self.c})"


foo_lib = ctypes.CDLL("./foo.so")

# Bad habit to not define the return type, especially for the `C pointer`.
# When return type is not defined, it will be automatically inferred as 4-byte int.
print(f"\n#1 Bad habit to not define the return type, especially for the `C pointer`.")

# Call the function
p_foo = foo_lib.create_foo()

print(f"p_foo: {hex(p_foo)}, !!!Only 4-byte address, it's danger in 64-bit system!!!")
# exception: Segmentation fault
# print(ctypes.cast(p_foo, ctypes.POINTER(Foo)).contents)


# Good habit to fully define argument types and return type
print(f"\n#2 Good habit to fully define argument types and return type.")
foo_lib.create_foo.argtypes = []
foo_lib.create_foo.restype = ctypes.c_void_p

# Call the function
p_foo = foo_lib.create_foo()

print(f"p_foo: {hex(p_foo)}, p_foo contents: {ctypes.cast(p_foo, ctypes.POINTER(Foo)).contents}")
print(f"p_foo: {hex(p_foo)}, p_foo contents: {Foo.from_address(p_foo)}")  # Or use `from_address()`


# Good habit to fully define argument types and return type
print(f"\n#3 Good habit to fully define argument types and return type.")
foo_lib.create_foo.argtypes = []
foo_lib.create_foo.restype = ctypes.POINTER(Foo)

p_foo = foo_lib.create_foo()
print(f"p_foo: {hex(ctypes.addressof(p_foo.contents))}, p_foo contents: {p_foo.contents}")
print(f"p_foo: {hex(ctypes.cast(p_foo, ctypes.c_void_p).value)}, p_foo contents: {p_foo.contents}")
