C_ARGS = -g -Wall -O3

CC = gcc

BINARY = udp_server udp_client tcp_server tcp_client

all: $(BINARY)

udp_server: udp_server.c
	$(CC) $(C_ARGS) -o $@ $^

udp_client: udp_client.c
	$(CC) $(C_ARGS) -o $@ $^

tcp_server: tcp_server.c
	$(CC) $(C_ARGS) -o $@ $^

tcp_client: tcp_client.c
	$(CC) $(C_ARGS) -o $@ $^

.PHONY: clean
clean:
	rm -f $(BINARY)
