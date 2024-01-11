"""
>>> chr(0x20ac)
'€'
>>> ord("€")
8364
>>> hex(ord("€"))
'0x20ac'
>>> "€".encode()
b'\xe2\x82\xac'
>>> ord("€") > 0x0800
True
>>> ord("€") < 0xFFFF
True
>>> ord("€")
8364
>>> hex(ord("€"))
'0x20ac'
>>> hex((ord("€") >> 12) | 0xe0)
'0xe2'
>>> hex((ord("€") >> 6) & 0x3f  | 0x80)
'0x82'
>>> hex((ord("€") >> 0) & 0x3f  | 0x80)
'0xac'
"""

import struct

# chr(0x20ac): codepoint -> charactor
# ord("€"): charactor -> codepoint
# "€".encode(): charactor -> binary
# utf8_codepoint_to_binary(): codepoint -> binary
# 0x20AC -> b'\xe2\x82\xac'
def utf8_codepoint_to_binary(cp:int) -> bytes:
    if cp > 0x0800 and cp < 0xffff:
        b1 = (cp >> 12) | 0xe0
        b2 = (cp >> 6) & 0x3f  | 0x80
        b3 = (cp >> 0) & 0x3f  | 0x80
        b = struct.pack("> BBB", b1, b2, b3)
    return b

assert chr(0x20ac) == "€"
assert ord("€") == 0x20ac
assert utf8_codepoint_to_binary(0x20ac) == "€".encode()