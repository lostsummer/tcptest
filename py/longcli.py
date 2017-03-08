#!/usr/bin/env python3

import asyncio
import uvloop
import sys
import transdata
import json
import time
import socket

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

global sentCount, rcvCount, succCount
sentCount = 0
rcvCount = 0
succCount = 0

async def request(host, port, dataSend):
    global sentCount, rcvCount, succCount
    connect = asyncio.open_connection(host, port)
    reader, writer = await connect
    try:
        while True:
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
    #except asyncio.TimeoutError:
    #    future.cancel()
    #    print("cancel!")
    except Exception:
        pass

    writer.close()
    connect.close()


if __name__ == '__main__':
    bf = transdata.TransData()
    bf.LoadJson('transdata.json')
    dataSend = bf.Pack()

    host = sys.argv[1]
    port = int(sys.argv[2])
    connCount = int(sys.argv[3])
    sendTime = float(sys.argv[4])
    loop = asyncio.get_event_loop()
    tasks = [request(host, port, dataSend)
             for i in range(connCount)]
    start = time.time()
    try:
        #loop.run_until_complete(asyncio.wait(tasks))
        loop.run_until_complete(asyncio.wait(tasks, timeout=sendTime))
    except KeyboardInterrupt:
        pass

    loop.stop()
    #loop.close()
    end = time.time()
    print("sent: {0}".format(sentCount))
    print("recv: {0}".format(rcvCount))
    print("success: {0}".format(succCount))
    print("cost time: {0} s".format(end - start))
    print("speed: {0} req/s".format(succCount/(end - start)))

