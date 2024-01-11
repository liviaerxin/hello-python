CC = gcc
CFLAGS = -Wall -fPIC
INCLUDE = -I/usr/include/python3.10

# Get all source files with a .c file extension
SOURCES = $(wildcard *.c)
# SOURCES = test.c

# Replace .c with .o for object files
OBJECTS = $(SOURCES:.c=.o)

DYLIBS = $(SOURCES:_module.c=.so)

all: $(DYLIBS)

# Rule to build object files
%.o: %.c
	$(CC) -c $(CFLAGS) $(INCLUDE) $< -o $@

%.so: %.o
	$(CC) -shared $< -o $@

# `import hello` will search `hello.so` in Linux.
run: $(DYLIBS)
	python3 -c 'import hello; hello.greet("it is me");'

clean:
	rm -f *.o *.so