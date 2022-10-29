import asyncio
import re

pattern = re.compile(r"(?P<method>[a-zA-Z]+) (?P<uri>(\w+://)?(?P<host>[^\s\'\"<>\[\]{}|/:]+)(:(?P<port>\d+))?[^\s\'\"<>\[\]{}|]*) ")


async def handle_conn(reader, writer):
    client_request = (await reader.readuntil(b"\r\n\r\n")).decode()
    print(client_request)
    
    if client_request.startswith("CONNECT"):
        request_regex = pattern.match(client_request)

        if request_regex:
            ws_reader, ws_writer = await asyncio.open_connection(request_regex.group("host"), request_regex.group("port"))
            print(request_regex.group("host"), request_regex.group("port"))
        else:
            writer.close()

        writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        await writer.drain()
        print("Connection made.")
    
        



async def main():
    server = await asyncio.start_server(handle_conn, "127.0.0.1", 8544)
    async with server:
        await server.serve_forever()

asyncio.run(main())