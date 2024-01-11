CC = gcc
CFLAGS = -Wall -fPIC
INCLUDE = -I/usr/include/python3.10/
LIBS = -L/usr/lib/x86_64-linux-gnu/ -lpython3.10

# Get all source files with a .c file extension
SOURCES = $(wildcard *.c)
# SOURCES = test.c

# Replace .c with .o for object files
OBJECTS = $(SOURCES:.c=.o)

DYLIBS = $(SOURCES:.c=.so)

# Define the executables based on the source files
EXECUTABLES = $(SOURCES:.c=.out)

all: $(DYLIBS)

# Rule to build each object file
%.o: %.c
	$(CC) -c $(CFLAGS) $(INCLUDE) $< -o $@

# Rule to build each shared library
%.so: %.o
	$(CC) -shared $< -o $@

# Rule to build each executable
exec: $(EXECUTABLES)

%.out: %.o
	$(CC) $< $(LIBS) -o $@

clean:
	rm -f $(OBJECTS) $(DYLIBS) $(EXECUTABLES)