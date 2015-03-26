#ifndef _VARGS_COUNT_
#define _VARGS_COUNT_

#define __VARGS_PREFIX_FUNC( \
	 _1,  _2,  _3,  _4,  _5,  _6,  _7,  _8, \
	 _9, _10, _11, _12, _13, _14, _15, _16, \
	_17, _18, _19, _20, _21, _22, _23, _24, \
	_25, _26, _27, _28, _29, _30, _31, _32, N, ...) N

#define __VARGS_SUFFIX \
	32, 31, 30, 29, 28, 27, 26, 25, \
	24, 23, 22, 21, 20, 19, 18, 17, \
	16, 15, 14, 13, 12, 11, 10,  9, \
	 8,  7,  6,  5,  4,  3,  2,  1, 0

#define __VARGS_COUNT(...) __VARGS_PREFIX_FUNC(__VA_ARGS__)

#define vargs_count(...) (__VARGS_COUNT(0, ##__VA_ARGS__, __VARGS_SUFFIX) - 1)

#endif //_VARGS_COUNT_
