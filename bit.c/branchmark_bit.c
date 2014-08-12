#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define clock_to_ms(x) ((x)/1000ul)

#include "bit.h"

#define ASSERT(exp, msg) \
do { \
	if (!(exp)) \
	{ \
		printf("Assert Failed: " #exp "\n  Msg: %s\n  Pos: %s: %s(): %d\n", msg, __FILE__, __FUNCTION__, __LINE__); \
		abort(); \
	} \
} while(0)

#define MAX_TEST_TIMES (10*1000*1000)

#define TEST_SIZE     129
#define TEST_BIT_LEN  (TEST_SIZE*8)
#define TEST_POS      517

static inline int bit_first_simple(const void *pData, size_t uLen)
{
	size_t i;
	for (i=0; i<uLen*8; i++)
		if (((const unsigned char *)pData)[i/8] & gs_cBitMasks[i%8])
			return i;
	return -1;
}

int main()
{
	char sBuf[TEST_SIZE] = {0};
	size_t i;
	clock_t bgn, end;
	
	for (i=0; i<sizeof(long)*8; i++)
	{
		int c = i/8*8+7-i%8;
		ASSERT(c == bit_first_in_long(1l<<i), "bit.first.long");
	}

	for (i=0; i<TEST_BIT_LEN; i++)
	{
		ASSERT(0 == bit_get(sBuf, i), "bit.get");
		ASSERT(1 == bit_set(sBuf, i, 1), "bit.set");
		ASSERT(1 == bit_get(sBuf, i), "bit.get");
		ASSERT(i == bit_first(sBuf, TEST_SIZE), "bit.first");
		ASSERT(0 == bit_set(sBuf, i, 0), "bit.set");
		ASSERT(0 == bit_get(sBuf, i), "bit.get");
	}
	
	for (i=0; i<TEST_BIT_LEN; i++)
		ASSERT(1 == bit_set(sBuf, i, 1), "bit.set");
	
	for (i=0; i<TEST_BIT_LEN; i++)
	{
		ASSERT(i == bit_first(sBuf, TEST_SIZE), "bit.first");
		ASSERT(i == bit_first_simple(sBuf, TEST_SIZE), "bit.first.simple");
		ASSERT(0 == bit_set(sBuf, i, 0), "bit.set");
	}
	
	ASSERT(-1 == bit_first(sBuf, TEST_SIZE), "bit.first");
	ASSERT(-1 == bit_first_simple(sBuf, TEST_SIZE), "bit.first.simple");
	
	ASSERT(1 == bit_set(sBuf, TEST_POS, 1), "bit.set");
	
	bgn = clock();
	for (i=0; i<MAX_TEST_TIMES; i++)
		ASSERT(TEST_POS == bit_first(sBuf, TEST_SIZE), "bit.first");
	end = clock();
	printf("%u \tbit_first(%u): \t%lums\n", MAX_TEST_TIMES, TEST_POS, clock_to_ms(end - bgn));
	
	bgn = clock();
	for (i=0; i<MAX_TEST_TIMES; i++)
		ASSERT(TEST_POS == bit_first_simple(sBuf, TEST_SIZE), "bit.first");
	end = clock();
	printf("%u \tbit_first_simple(%u): \t%lums\n", MAX_TEST_TIMES, TEST_POS, clock_to_ms(end - bgn));

	return 0;
}
