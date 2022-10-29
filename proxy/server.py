import asyncio
import re

request_pattern = re.compile(r"(?P<method>[a-zA-Z]+) (?P<uri>(\w+://)?(?P<host>[^\s\'\"<>\[\]{}|/:]+)(:(?P<port>\d+))?[^\s\'\"<>\[\]{}|]*) ")

async def transfer_stream(reader, writer, close_event):
    while not close_event.is_set():
        try:
            data = await asyncio.wait_for(reader.read(1024), 1)
        except asyncio.TimeoutError:
            continue
        
        if data == b"":
            close_event.set()
            print("Connection closed.")
            break
            
        writer.write(data)
        await writer.drain()

async def handle_conn(reader, writer):
    client_request = (await reader.readuntil(b"\r\n\r\n")).decode()
    if client_request.startswith("CONNECT"):
        request_regex = request_pattern.match(client_request)
        if request_regex:
            ws_reader, ws_writer = await asyncio.open_connection(request_regex.group("host"), request_regex.group("port"))
            print("Connecting to", request_regex.group("host"), ":", request_regex.group("port"))
            writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await writer.drain()
            print("Connection made.")
            close_event = asyncio.Event()
            await asyncio.gather(transfer_stream(reader, ws_writer, close_event),
                transfer_stream(ws_reader, writer, close_event))
    writer.close()

async def main():
    server = await asyncio.start_server(handle_conn, "127.0.0.1", 8544)
    async with server:
        await server.serve_forever()

asyncio.run(main())
