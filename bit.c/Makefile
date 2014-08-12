C_ARGS = -g -Wall -O3

CC = gcc

BINARY = branchmark_bit

.SUFFIXES: .o .c

.c.o:
	$(CC) $(C_ARGS) -c $^

all: $(BINARY)

branchmark_bit: branchmark_bit.o
	$(CC) $(C_ARGS) -o $@ $^

.PHONY: clean test
clean:
	rm -f $(BINARY) *.o
test: $(BINARY)
	./branchmark_bit
