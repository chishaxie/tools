C_ARGS = -g -Wall

CC = gcc
CX = g++

BINARY = top-k top-k2

all: $(BINARY)

top-k: stochastic-top-k.h top-k.cpp
	$(CX) $(C_ARGS) -o $@ top-k.cpp

top-k2: stream-top-k.h top-k.cpp
	$(CX) $(C_ARGS) -o $@ -DSTREAM top-k.cpp
	
strip:
	strip $(BINARY)

.PHONY: clean
clean:
	rm -f $(BINARY)
