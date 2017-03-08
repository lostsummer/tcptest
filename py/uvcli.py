#!/usr/bin/env python3

import asyncio
import uvloop
import sys
import transdata
import json
import time

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

global sentCount, rcvCount, succCount
sentCount = 0
rcvCount = 0
succCount = 0

async def request(host, port, dataSend):
    global sentCount, rcvCount, succCount
    try:
        connect = asyncio.open_connection(host, port)
        reader, writer = await connect
        writer.write(dataSend)
        sentCount += 1
        await writer.drain()
        dataRcv = await reader.read(1024)
        rcvCount += 1
        sendBuf = transdata.TransData()
        sendBuf.Read(dataSend)
        rcvBuf = transdata.TransData()
        rcvBuf.Read(dataRcv)
        if (rcvBuf.head.head_id == 34969) and \
                (rcvBuf.head.data_len == len(dataRcv) - 10) and \
                (rcvBuf.head.data_type - sendBuf.head.data_type == 100):
            succCount += 1

    except Exception as e:
        print(e, file=sys.stderr)
        return

    writer.close()
    connect.close()


if __name__ == '__main__':
    bf = transdata.TransData()
    bf.LoadJson('transdata.json')
    dataSend = bf.Pack()

    host = sys.argv[1]
    port = int(sys.argv[2])
    connCount = int(sys.argv[3])
    repeatTime = int(sys.argv[4])
    loop = asyncio.get_event_loop()
    start = time.time()
    for i in range(repeatTime):
        tasks = [request(host, port, dataSend)
                 for i in range(connCount)]
        loop.run_until_complete(asyncio.wait(tasks))

    loop.close()
    end = time.time()

    print("sent: {0}".format(sentCount))
    print("recv: {0}".format(rcvCount))
    print("success: {0}".format(succCount))
    print("cost time: {0} s".format(end - start))

