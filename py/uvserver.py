#!/usr/bin/env python3

import asyncio
import uvloop
import sys
import transdata

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

global cli_connected
global cli_received
cli_connected = 0
cli_received = 0


class TestProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        #peername = transport.get_extra_info('peername')
        #print('Connection from {}'.format(peername))
        self.transport = transport
        global cli_connected
        cli_connected += 1

    def data_received(self, data):
        if not data:
            self.transport.close()
            print('here')
            return

        rcvData = transdata.TransData()
        rcvData.Read(data)
        sendData = rcvData
        sendData.head.data_type += 100
        data = sendData.Pack()
        self.transport.write(data)
        global cli_received
        cli_received += 1

if __name__ == '__main__':
    # host = sys.argv[1]
    host = "0.0.0.0"
    port = int(sys.argv[1])
    loop = asyncio.get_event_loop()
    # Each client connection will create a new protocol instance
    coro = loop.create_server(TestProtocol, host, port)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
    print("")
    print("connected: {0}".format(cli_connected))
    print("received: {0}".format(cli_received))
