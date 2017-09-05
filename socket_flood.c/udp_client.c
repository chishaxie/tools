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

int g_int = 0;

void signal_func(int signal_num)
{
    gettimeofday(&g_end, NULL);
    long us = 1000000 * (g_end.tv_sec - g_bgn.tv_sec) + g_end.tv_usec - g_bgn.tv_usec;
    printf("\n");
    printf("%ld func\n", g_call);
    printf("%zu bytes (%zu KB, %zu MB)\n", g_bytes, g_bytes / 1024, g_bytes / 1024 / 1024);
    printf("%ld us (%ld s)\n", us, us / 1000000);
    printf("%lf KB/s (%lf MB/s)\n", g_bytes / 1024.0 * 1000000 / us, g_bytes / 1024.0 / 1024 * 1000000 / us);
    // _exit(0);
    g_int = 1;
}

int main(int argc, char const *argv[])
{
    if (argc < 4) {
        printf("Usage: %s <ip> <port> <bytes>\n", argv[0]);
        return 1;
    }

    int port = atoi(argv[2]);
    size_t bytes = atoi(argv[3]);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = inet_addr(argv[1]);
    addr.sin_port = htons(port);

    int ret;
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    ASSERT(sock > 0);

    char msg[65536] = {0};
    ASSERT(bytes <= sizeof(msg));

    signal(SIGINT, signal_func);

    gettimeofday(&g_bgn, NULL);

    while (!g_int) {
        ret = sendto(sock, msg, bytes, 0, (struct sockaddr *)&addr,sizeof(addr));
        ASSERT(ret > 0);
        g_bytes += ret;
        g_call ++;
    }

    ret = sendto(sock, "fin", 3, 0, (struct sockaddr *)&addr,sizeof(addr));
    ASSERT(ret > 0);

    return 0;
}
