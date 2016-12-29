#include "get_exe_path.h"
#include "get_os.h"

#if defined(Q_OS_LINUX)
#   include <unistd.h>
#elif defined(Q_OS_DARWIN)
#   include <mach-o/dyld.h>
#   include <limits.h>
#   include <stdlib.h>
#   include <string.h>
#endif

int get_executable_path(char *szStr, unsigned int uStrSize)
{
    szStr[0] = '\0';

#if defined(Q_OS_LINUX)
    readlink("/proc/self/exe", szStr, uStrSize);

#elif defined(Q_OS_DARWIN)
    char szOrgPath[PATH_MAX];
    char szPath[PATH_MAX];
    unsigned uSize = sizeof(szOrgPath);
    _NSGetExecutablePath(szOrgPath, &uSize);
    realpath(szOrgPath, szPath);
    strncpy(szStr, szPath, uStrSize);

#endif

    if (szStr[0] != '\0')
        return 0;
    else
        return -1;
}
