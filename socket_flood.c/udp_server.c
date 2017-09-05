#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/time.h>

#define ASSERT(x) \
    do { \
        if (!(x)) { \
            fprintf(stderr, "ASSERT failed: \"" #x "\" line %d\n", __LINE__); \
            _exit(1); \
        } \
    } while(0)

long g_call = 0;
size_t g_bytes = 0;
struct timeval g_bgn;
struct timeval g_end;

void signal_func(int signal_num)
{
    gettimeofday(&g_end, NULL);
    long us = 1000000 * (g_end.tv_sec - g_bgn.tv_sec) + g_end.tv_usec - g_bgn.tv_usec;
    printf("\n");
    printf("%ld func\n", g_call);
    printf("%zu bytes (%zu KB, %zu MB)\n", g_bytes, g_bytes / 1024, g_bytes / 1024 / 1024);
    printf("%ld us (%ld s)\n", us, us / 1000000);
    printf("%lf KB/s (%lf MB/s)\n", g_bytes / 1024.0 * 1000000 / us, g_bytes / 1024.0 / 1024 * 1000000 / us);
    _exit(0);
}

int main(int argc, char const *argv[])
{
    if (argc < 2) {
        printf("Usage: %s <port>\n", argv[0]);
        return 1;
    }

    int port = atoi(argv[1]);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);

    int ret;
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    ASSERT(sock > 0);
    ret = bind(sock, (struct sockaddr *)&addr, sizeof(addr));
    ASSERT(ret == 0);

    signal(SIGINT, signal_func);

    gettimeofday(&g_bgn, NULL);

    char msg[65536];
    for (;;) {
        socklen_t addr_len = sizeof(addr);
        ret = recvfrom(sock, msg, sizeof(msg), 0, (struct sockaddr *)&addr, &addr_len);
        ASSERT(ret > 0);
        if (ret == 3 && memcmp(msg, "fin", 3) == 0)
            signal_func(0);
        if (g_bytes == 0)
            gettimeofday(&g_bgn, NULL);
        g_bytes += ret;
        g_call ++;
    }

    return 0;
}
