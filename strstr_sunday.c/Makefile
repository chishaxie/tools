C_ARGS = -O2 -g -Wall

CX = gcc

BIN = demo

all: $(BIN)

demo: demo.o strstr_sunday.o
	$(CX) $(C_ARGS) -o $@ $^

.SUFFIXES: .o .c

.c.o:
	$(CX) $(C_ARGS) -c $^

.PHONY: clean

clean:
	rm -f $(BIN) *.o
