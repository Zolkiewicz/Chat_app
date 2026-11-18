import asyncio
import websockets

MESSAGES = [
    "Message-1",
    "Message-2",
    "Message-3",
    "Message-4",
    "Message-5",
]

async def run_tcp_demo():
    print("\n\nTCP\n")
    received_chunks = []

    async def tcp_handler(reader, writer):
        while True:
            data = await reader.read(1024)
            if not data:
                break
            received_chunks.append(data.decode())
        writer.close()

    server = await asyncio.start_server(tcp_handler, "127.0.0.1", 8888)

    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)

    for msg in MESSAGES:
        writer.write(msg.encode())
        await writer.drain()

    writer.close()
    await writer.wait_closed()
    await asyncio.sleep(0.1)
    server.close()
    await server.wait_closed()

    print(f"Sent {len(MESSAGES)} separate messages.")
    print(f"TCP Server read {len(received_chunks)} chunks:")
    for idx, chunk in enumerate(received_chunks, 1):
        print(f"Chunk {idx}: {chunk!r}\n")

async def run_websocket_demo():
    print("\n\nWEBSOCKET\n")
    received_messages = []

    async def ws_handler(websocket):
        async for message in websocket:
            received_messages.append(message)

    server = await websockets.serve(ws_handler, "127.0.0.1", 8765)

    async with websockets.connect("ws://127.0.0.1:8765") as ws:
        for msg in MESSAGES:
            await ws.send(msg)

    await asyncio.sleep(0.1)
    server.close()
    await server.wait_closed()

    print(f"Sent {len(MESSAGES)} separate messages.")
    print(f"WebSocket Server received {len(received_messages)} distinct message(s):")
    for idx, msg in enumerate(received_messages, 1):
        print(f"Msg {idx}: {msg!r}\n")


async def main():
    await run_tcp_demo()
    await run_websocket_demo()


if __name__ == "__main__":
    asyncio.run(main())


# MESSAGES = [
#     "Message-1",
#     "Message-2",
#     "Message-3",
#     "very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very long message-4",
#     "Message-5",
# ]
