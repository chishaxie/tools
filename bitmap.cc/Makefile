C_ARGS = -g -Wall

CC = gcc
CX = g++

BINARY = bitmap_unit_test

all: $(BINARY)

bitmap_unit_test: bitmap_unit_test.o
	$(CX) $(C_ARGS) -o $@ $^
	
bitmap_unit_test.o: bitmap_unit_test.cpp bitmap.h
	$(CX) $(C_ARGS) -c -o $@ bitmap_unit_test.cpp

.PHONY: clean
clean:
	rm -f $(BINARY) *.o
