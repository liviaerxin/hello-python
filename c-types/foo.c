#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int a;
    double b;
    long c;
} Foo;

Foo* create_foo() {
    Foo* foo = malloc(sizeof(Foo));
    foo->a = 1;
    foo->b = 2.0;
    foo->c = 3;
    printf("Foo address: %p\n", foo);
    return foo;
}

int main() {
    Foo* foo = create_foo();
    printf("Foo values: %d, %f, %ld\n", foo->a, foo->b, foo->c);
    
    return 0;
}