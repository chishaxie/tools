#include <stdio.h>
#include <stdlib.h>

#include "vargs_count.h"

#define CHECK(x) \
do { \
	if (!(x)) \
	{ \
		fprintf(stderr, "Check \"" #x "\" failed.\n"); \
		abort(); \
	} \
} while(0)

int main()
{
	CHECK(vargs_count() == 0);
	CHECK(vargs_count(1) == 1);
	CHECK(vargs_count(1, 2) == 2);
	CHECK(vargs_count(1, 2, 3) == 3);
	CHECK(vargs_count(1, 2, 3, 4) == 4);
	CHECK(vargs_count(1, 2, 3, 4, 5) == 5);
	CHECK(vargs_count(1, 2, 3, 4, 5, 6) == 6);
	CHECK(vargs_count(1, 2, 3, 4, 5, 6, 7) == 7);
	CHECK(vargs_count(1, 2, 3, 4, 5, 6, 7, 8) == 8);
	return 0;
}
