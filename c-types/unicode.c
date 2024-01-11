// Do in python 3.10
#include <Python.h>
#include <stdio.h>
#include <wchar.h>
#include <locale.h>

int main(){
    // Char*
    char *str = "Hello, World 你!";
    // str will be utf-8 encoding bytes in memory, not the unicode code points.
    // strlen() returns the length of the encoding bytes, such as, `你` will occupy 3-byte size.
    printf("%s, %zu\n", str, strlen(str));


    // In Python.
    PyObject* op= PyUnicode_FromStringAndSize(str, strlen(str));
    
    // It's the length of the unicode characters. such as, `你` will 1 size.
    PyASCIIObject* ascii_op= ((PyASCIIObject*)op);
    printf("length: %zu, kind: %u, compact: %u, ascii: %u, ready: %u\n\n", ascii_op->length, ascii_op->state.kind, ascii_op->state.compact, ascii_op->state.ascii, ascii_op->state.ready);

    // WChar*
    setlocale(LC_ALL, "C.UTF-8");
    wchar_t* myWideChar = L"Hello, World 你!";
    // wchar_t's str will be unicode point in memory, not the utf-8 encoding bytes.
    // wcslen() returns the length of the unicode characters, such as, `你` will be 1 size.
    printf("Size of wchar_t: %zu bytes\n", sizeof(wchar_t));
    printf("%ls, %zu characters\n", myWideChar, wcslen(myWideChar));

    char* wp = (char*)(myWideChar); // "H": '0x48' in code point
    // %hh: unsigned char, %x: hex
    printf("Inspect wchar[0] 4-bytes: 0x%hhx 0x%hhx 0x%hhx 0x%hhx\n", *wp, *(wp+1), *(wp+2), *(wp+3));

    wp = (char*)(myWideChar+13); // "你": '0x4f60' in code point
    printf("Inspect wchar[13] 4-bytes: 0x%hhx 0x%hhx 0x%hhx 0x%hhx\n", *wp, *(wp+1), *(wp+2), *(wp+3));
    
    return 0;
}