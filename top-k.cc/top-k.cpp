#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <signal.h>

#ifdef STREAM
#include "stream-top-k.h"
#else
#include "stochastic-top-k.h"
#endif

char line[128];

int g_exit = 0;

void signal_exit(int s)
{
	g_exit = 1;
}

int main(int argc, char *argv[])
{
	int top = 100, capacity = 10000;
	int ret;
	uint64_t ddwValue;
	uint64_t *outValue;
	long *outCount;
	
	char strCount[10];
	int strCountLen;
	
	ITopK<uint64_t> *topper;
	
	if (argc > 1)
	{
		if (argc == 2 && (0 == strcmp(argv[1], "-h") || 0 == strcmp(argv[1], "--help")))
		{
			fprintf(stderr, "This is a tools to estimate top-k of stream numbers.\n");
			fprintf(stderr, "    Usage: %s [capacity] [k]\n", argv[0]);
			fprintf(stderr, "      Default: capacity=%d k=%d\n", capacity, top);
			exit(1);
		}
		
		capacity = atoi(argv[1]);
		if (capacity <= 0)
			capacity = 10000;
		
		if (argc > 2)
		{
			top = atoi(argv[2]);
			if (top <= 0)
				top = 100;
		}
	}

#ifdef STREAM
	topper = new StreamTopper<uint64_t>(capacity);
#else
	topper = new StochasticTopper<uint64_t>(capacity);
#endif

	outValue = new uint64_t[top];
	outCount = new long[top];
	
	fprintf(stderr, "capacity: %d, top-k: %d\n", capacity, top);
	
	signal(SIGINT, signal_exit);
	signal(SIGTERM, signal_exit);
	
	for (;;)
	{
		if (g_exit)
			break;
		
		fgets(line, sizeof(line), stdin);
		
		if (feof(stdin))
			break;

#if defined(__LP64__) || defined(__64BIT__) || defined(_LP64) || (__WORDSIZE==64)
		if ( 1 != sscanf(line, "%lu", &ddwValue) )
#else
		if ( 1 != sscanf(line, "%llu", &ddwValue) )
#endif
		{
			fprintf(stderr, "Format Error\n");
			exit(1);
		}
		
		topper->offer(ddwValue);
	}
	
	ret = topper->peek(top, outValue, outCount);
	printf("[top %d in %ld]\n", ret, topper->totalCount());
	
	for (int i=0; i<ret; i++){
		strCountLen = snprintf(strCount, sizeof(strCount), "%ld", outCount[i]);
		for (int j=strCountLen + 1; j<(int)sizeof(strCount); j++)
			printf(" ");
#if defined(__LP64__) || defined(__64BIT__) || defined(_LP64) || (__WORDSIZE==64)
		printf("%s %lu\n", strCount, outValue[i]);
#else
		printf("%s %llu\n", strCount, outValue[i]);
#endif
	}
		
	delete [] outValue;
	delete [] outCount;
	delete topper;
		
	return 0;
}
