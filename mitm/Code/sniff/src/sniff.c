#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <netinet/in.h>
#include <errno.h>
#include <netdb.h>

#include <netinet/ip.h>         
#include <net/ethernet.h> 
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/ioctl.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <linux/if_packet.h>

struct sockaddr_in source,dest;
// int tcp=0,udp=0,icmp=0,others=0,igmp=0,total=0,i,j;

void relay_icmp_packet(int sockid, unsigned char* buffer, int size)
{
    struct ethhdr *eth = (struct ethhdr *)buffer;
    struct iphdr *iph = (struct iphdr *)(buffer + sizeof(struct ethhdr));
    unsigned short iphdrlen =iph->ihl*4;

    if (iph->protocol != 1) return;

    memset(&source, 0, sizeof(source));
    source.sin_addr.s_addr = iph->saddr;

    eth->h_source[0] = 0X02;
    eth->h_source[1] = 0X42;
    eth->h_source[2] = 0X0A;
    eth->h_source[3] = 0X09;
    eth->h_source[4] = 0X00;
    eth->h_source[5] = 0X69;

    if (iph->saddr == inet_addr("10.9.0.5")
        && iph->daddr == inet_addr("10.9.0.6")) {
        eth->h_dest[0] = 0X02;
        eth->h_dest[1] = 0X42;
        eth->h_dest[2] = 0X0A;
        eth->h_dest[3] = 0X09;
        eth->h_dest[4] = 0X00;
        eth->h_dest[5] = 0X06;
    } else if (iph->saddr == inet_addr ("10.9.0.6")
        && iph->daddr == inet_addr ("10.9.0.5")) {
        eth->h_dest[0] = 0X02;
        eth->h_dest[1] = 0X42;
        eth->h_dest[2] = 0X0A;
        eth->h_dest[3] = 0X09;
        eth->h_dest[4] = 0X00;
        eth->h_dest[5] = 0X05;
    } else {
        printf("return\n");
        return;
    }

    struct sockaddr_ll device;
    memset(&device, 0, sizeof device);
    device.sll_ifindex = if_nametoindex("eth0");

    int ret = -5;
    ret = sendto(sockid, eth, size, 0, (const struct sockaddr *)&device, sizeof(device));

    if (ret)
        printf("Echo request sent from %.2X:%.2X:%.2X:%.2X:%.2X:%.2X to %.2X:%.2X:%.2X:%.2X:%.2X:%.2X\n",
               eth->h_source[0], eth->h_source[1], eth->h_source[2],
               eth->h_source[3], eth->h_source[4], eth->h_source[5],
               eth->h_dest[0], eth->h_dest[1], eth->h_dest[2],
               eth->h_dest[3], eth->h_dest[4], eth->h_dest[5]);
}
