#!/usr/bin/env python3

import multiprocessing
import socket
import sys
import transdata


def do_accept(s):
    while True:
        conn, addr = s.accept()
        conn.settimeout(1)
        data = conn.recv(1024)
        while data:
            sendbuf = transdata.TransData()
            sendbuf.Read(data)
            sendbuf.head.data_type += 100
            conn.send(sendbuf.Pack())
            data = conn.recv(1024)
        conn.close()

port = int(sys.argv[1])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', port))
s.listen(1024)
pool = multiprocessing.Pool(processes = 4)
try:
    for i in range(4):
        pool.apply_async(do_accept, (s,))

    pool.close()
    pool.join()

except KeyboardInterrupt:
    pass

