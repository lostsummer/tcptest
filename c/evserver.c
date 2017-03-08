#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <assert.h>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <signal.h>

#include <event2/event.h>
#include <event2/bufferevent.h>
#include "transdata.h"

#define SERV_PORT 9877
#define LISTEN_BACKLOG 128
#define BUF_LEN 1024
#define MAX_FDSIZE 200000

static int accepted = 0;
static int received = 0;
static int sent = 0;

void do_accetp(evutil_socket_t listenfd, short event, void *arg);
void read_cb(struct bufferevent *bev, void *arg);
void error_cb(struct bufferevent *bev, short event, void *arg);
void write_cb(struct bufferevent *bev, void *arg);

void my_handler(int s)
{
	printf("caught signal %d\n", s);
    printf("accepted: %d\n", accepted);
    printf("received: %d\n", received);
    printf("sent: %d\n", sent);
	exit(1);
}

int main(int argc, int **argv)
{
	int server_port = 0;
	if (argc < 2)
		server_port = SERV_PORT;
	else
		server_port = atoi(argv[1]);

	struct sigaction my_sigact;
	my_sigact.sa_handler = my_handler;
	sigemptyset(&my_sigact.sa_mask);
	my_sigact.sa_flags = 0;
	sigaction(SIGINT, &my_sigact, NULL);

    evutil_socket_t listenfd;
    if((listenfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("socket\n");
        return 1;
    }

    struct sockaddr_in servaddr;
    bzero(&servaddr, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(server_port);

    if(bind(listenfd, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("bind\n");
        return 1;
    }
    if(listen(listenfd, LISTEN_BACKLOG) < 0)
    {
        perror("listen\n");
        return 1;
    }

    printf("Listening at %d...\n", server_port);

    evutil_make_listen_socket_reuseable(listenfd);
    evutil_make_socket_nonblocking(listenfd);

    struct event_base *base = event_base_new();
    if(base == NULL)
    {
        perror("event_base\n");
        return 1;
    }
    const char *eventMechanism = event_base_get_method(base);
    printf("Event mechanism used is %s\n", eventMechanism);

    struct event *listen_event;
    listen_event = event_new(base, listenfd, EV_READ | EV_PERSIST, do_accetp, (void *)base);
    event_add(listen_event, NULL);
    event_base_dispatch(base);

    if(close(listenfd) < 0)
    {
        perror("close\n");
        return 1;
    }
    printf("The End\n");
    printf("accepted: %d\n", accepted);
    printf("received: %d\n", received);
    printf("sent: %d\n", sent);
    return 0;
}

void do_accetp(evutil_socket_t listenfd, short event, void *arg)
{
    struct event_base *base = (struct event_base *)arg;
    evutil_socket_t fd;
    struct sockaddr_in cliaddr;
    socklen_t clilen;
    fd = accept(listenfd, (struct sockaddr *) &cliaddr, &clilen);
    if(fd < 0)
    {
        perror("accept\n");
        return;
    }
    if(fd > MAX_FDSIZE)
    {
        perror("fd > MAX_FDSIZE");
        if(close(fd) < 0)
        {
            perror("close\n");
            return;
        }
        return;
    }
    
    struct bufferevent *bev = bufferevent_socket_new(base, fd, BEV_OPT_CLOSE_ON_FREE);
    bufferevent_setcb(bev, read_cb, NULL, error_cb, arg);
    bufferevent_enable(bev, EV_READ | EV_WRITE | EV_PERSIST);
	accepted += 1;
}
    
void read_cb(struct bufferevent *bev, void *arg)
{
    char buf[BUF_LEN];
    int n;
    evutil_socket_t fd = bufferevent_getfd(bev);

	received += 1;
    while((n = bufferevent_read(bev, buf, BUF_LEN)) > 0 && (n < 1024))
    {
        buf[n] = '\0';
		TRANS_DATA *p_trans_data = (TRANS_DATA *)buf;

		if (n < 10)
			return;
		else if (n < p_trans_data->head.data_len + 10)
			return;
		else if (p_trans_data->head.head_id != 34969)  //0x99 0x88 little endian
			return;

		p_trans_data->head.data_type += 100;
        bufferevent_write(bev, buf, n);
		sent += 1;
    }
}

void error_cb(struct bufferevent *bev, short event, void *arg)
{
    evutil_socket_t fd = bufferevent_getfd(bev);
    //printf("fd = %u, ", fd);
    if(event & BEV_EVENT_TIMEOUT)
        //printf("Time out.\n");  // if bufferevent_set_timeouts() is called
		;
    else if(event & BEV_EVENT_EOF)
        //printf("Connection closed.\n");
		;
    else if(event & BEV_EVENT_ERROR)
        //printf("Some other error.\n");
		;
    bufferevent_free(bev);
}

void write_cb(struct bufferevent *bev, void *arg)
{
    // leave blank
}
