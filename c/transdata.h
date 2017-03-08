#ifndef _TRANSDATA_H_
#define _TRANSDATA_H_
#define PACKED __attribute__((aligned(1),packed))

typedef struct {
	unsigned short head_id;
	unsigned short data_type;
	unsigned int data_id;
	unsigned short data_len;
} PACKED HEAD; 

typedef struct {
	HEAD head;
	unsigned short content_len;
	unsigned char content[];
} PACKED TRANS_DATA; 

#endif
