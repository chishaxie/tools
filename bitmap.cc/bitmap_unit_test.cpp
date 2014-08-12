#include <stdio.h>

#include "bitmap.h"

int main()
{
	char sBuf[256];
	Bitmap<int> bm(-100, 1000, sBuf, sizeof(sBuf));
	
	printf("size: %zd\n", bm.size());
	printf("count: %zd\n", bm.count());
	
	bm.reset();
	bm[777] = bm[666] = true;
	
	printf("true: ");
	for (int i = bm.min(); i <= bm.max(); i ++)
		if (bm[i])
			printf("%d ", i);
	printf("\n");
	
	bm.set();
	bm[555] = bm[444] = false;
	bm.flip();
	bm.flip(444);
	bm[333].flip();
	
	printf("true: ");
	for (int i = bm.min(); i <= bm.max(); i ++)
		if (bm[i])
			printf("%d ", i);
	printf("\n");
	
	try {
		printf("bm[-100]: %d\n", (bool)bm[-100]);
		printf("bm[-101]: %d\n", (bool)bm[-101]);
	} catch (int x) {
		printf("catch: %d\n", x);
	}
	
	try {
		printf("bm[1000]: %d\n", (bool)bm[1000]);
		printf("bm[1001]: %d\n", (bool)bm[1001]);
	} catch (int x) {
		printf("catch: %d\n", x);
	}
	
	Bitmap<char> bm2;
	
	printf("bm2.count(): %zd\n", bm2.count());
	printf("bm2.size(): %zd\n", bm2.size());
	
	return 0;
}
