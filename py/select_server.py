#!/usr/bin/env python
import socket,select
import sys
import queue
import transdata

port = int(sys.argv[1])
conn_que = {}
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind(('',port))
sock.listen(100)
sock.setblocking(False)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
inputs=[sock]
outputs = []
timeout = 1
buf = transdata.TransData()
while 1:
    rs,ws,es=select.select(inputs,outputs,inputs,timeout)

    if not (rs or ws or es):
        continue

    for r in rs:
        if r is sock:
            clientsock,clientaddr=r.accept();
            #clientsock.setblocking(False)
            inputs.append(clientsock);
            conn_que[clientsock] = queue.Queue()
        else:
            data = r.recv(1024);
            if not data:
                inputs.remove(r)
                if r in outputs:
                    outputs.remove(r)

                r.close()
                del conn_que[r]

            else:
                conn_que[r].put(data)
                if r not in outputs:
                    outputs.append(r)

    for w in ws:
        try:
            data = conn_que[w].get_nowait()
        except queue.Empty:
            ws.remove(w)
        except KeyError:
            pass
        else:
            buf.Read(data)
            buf.head.data_type += 100
            w.send(buf.Pack())

    for e in es:
        if e in inputs:
            inputs.remove(e)
        if e in outputs:
            outputs.remove(e)

        e.close()
        del conn_que[e]


