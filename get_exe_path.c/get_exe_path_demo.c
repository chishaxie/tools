//gcc -o get_exe_path_demo -O3 -g -Wall get_exe_path_demo.c get_exe_path.c

#include <stdio.h>

#include "get_exe_path.h"

int main(int argc, char const *argv[])
{
    char szStr[4096];
    get_executable_path(szStr, sizeof(szStr));
    printf("%s\n", szStr);
    return 0;
}
