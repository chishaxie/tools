#include <string.h>

const int CSIZE = 256; // size of whole character set

/**
 * preprocessing step for sunday algorithm
 * calculate bad-character shift table
 */
static void prepare(const char *target, int m, int bad_table[])
{
    int i;
    for (i = 0; i < CSIZE; ++i) {
        bad_table[i] = m + 1;
    }
    for (i = 0; i < m; ++i) {
        bad_table[(unsigned)target[i]] = m - i;
    }
}

/**
 * strstr function implemented using sunday algorithm
 */
const char * strstr_sunday(const char *str, const char *target)
{
    if (NULL == str || NULL == target) {
        return NULL;
    }

    int n, m;
    n = strlen(str);
    m = strlen(target);

    if (!m) return str;
    if (!n) return NULL;

    /* preprocessing */
    int bad_table[CSIZE];
    prepare(target, m, bad_table);

    /* searching */
    int i = 0;
    while (i <= n - m) {
        if (memcmp(target, str + i, m) == 0) {
            return str + i;
        }

        i += bad_table[(unsigned)str[i + m]];
    }

    return NULL;
}
