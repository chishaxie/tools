#ifndef __BIT_H__
#define __BIT_H__

#include <stddef.h>

/* Just for Little Endian */

static const int gs_iBitFirsts[] = {
	0, 7, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4,
	3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
	2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
	2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

static const unsigned char gs_cBitMasks[] = {
	0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01
};

static inline int bit_first_in_long(unsigned long lData) //make sure ==> lData != 0
{
	int iRet = 0;
#if defined(__LP64__) || defined(__64BIT__) || defined(_LP64) || (__WORDSIZE==64)
	if ((lData & 0xffffffffl) == 0)
	{
		lData >>= 32;
		iRet += 32;
	}
#endif
	if ((lData & 0xffff) == 0)
	{
		lData >>= 16;
		iRet += 16;
	}
	if ((lData & 0xff) == 0)
	{
		lData >>= 8;
		iRet += 8;
	}
	return iRet + gs_iBitFirsts[lData % 256];
}

/* Find min(pos) Where bit = 1 */
static inline int bit_first(const void *pData, size_t uLen)
{
	int iRet = 0;
	while (uLen >= sizeof(long))
	{
		unsigned long lCur = *(const unsigned long *)pData;
		if (lCur)
			return iRet + bit_first_in_long(lCur);
		iRet += sizeof(long) * 8;
		uLen -= sizeof(long);
		pData = (const char *)pData + sizeof(long);
	}
	if (uLen > 0)
	{
		unsigned long lCur = 0;
		memcpy(&lCur, pData, uLen);
		if (lCur)
			return iRet + bit_first_in_long(lCur);
	}
	return -1;
}

/* Set bit */
static inline int bit_set(void *pData, size_t uPos, int iVal)
{
	if (iVal)
		((unsigned char *)pData)[uPos/8] |= gs_cBitMasks[uPos%8];
	else
		((unsigned char *)pData)[uPos/8] &= ~gs_cBitMasks[uPos%8];
	return iVal;
}

/* Get bit */
static inline int bit_get(const void *pData, size_t uPos)
{
	if (((const unsigned char *)pData)[uPos/8] & gs_cBitMasks[uPos%8])
		return 1;
	else
		return 0;
}

#endif
