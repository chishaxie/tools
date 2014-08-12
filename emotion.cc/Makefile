C_ARGS = -O3 -g -Wall

CX = g++

BIN = emotion_test emotion_benchmark

all: $(BIN)

emotion_test: emotion_test.o emotion_code.o
	$(CX) $(C_ARGS) -o $@ $^

emotion_benchmark: emotion_benchmark.o emotion_code.o
	$(CX) $(C_ARGS) -o $@ $^
	
.SUFFIXES: .o .cpp

.cpp.o:
	$(CX) $(C_ARGS) -c $^

.PHONY: clean

clean:
	rm -f $(BIN) *.o
