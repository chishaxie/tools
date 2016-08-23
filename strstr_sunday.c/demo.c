#include <stdio.h>
#include <string.h>

#include "strstr_sunday.h"

#define ASSERT(x) \
do { \
    if (!(x)) \
        fprintf(stderr, "[ASSERT]: " #x " failed at " __FILE__ ":%u\n", __LINE__); \
} while(0)

int main(int argc, char const *argv[])
{
    const char *str, *target;

    str = "aaabbbccchelloxxx";
    target = "hello";
    ASSERT(strstr(str, target) == strstr_sunday(str, target));

    str = "aaabbbccchelloxxx";
    target = "hello2";
    ASSERT(strstr(str, target) == strstr_sunday(str, target));

    str = "aaabhellobbccchelloxxx";
    target = "hello";
    ASSERT(strstr(str, target) == strstr_sunday(str, target));

    return 0;
}
