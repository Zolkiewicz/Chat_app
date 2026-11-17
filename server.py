import socket
import threading
from protocol import encode_message, decode_messages, ENCODING

HOST = '127.0.0.1'
PORT = 5555

clients = []
clients_lock = threading.Lock()

def broadcast(message_bytes: bytes, sender_socket = None):
    """Sends a message to all connected clients."""
    with clients_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.sendall(message_bytes)
                except OSError:
                    pass

def handle_client(conn: socket.socket, addr):
    print(f"[NEW CONNECTION] {addr}")
    buffer = ""
    
    with clients_lock:
        clients.append(conn)

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            buffer += data.decode(ENCODING)
            messages, buffer = decode_messages(buffer)
            
            for msg in messages:
                process_command(conn, addr, msg)
                
    except ConnectionResetError:
        pass
    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"[DISCONNECTED] {addr}")

def process_command(conn: socket.socket, addr, msg: dict):
    msg_type = msg.get("type")
    payload = msg.get("payload", {})

    if msg_type == "CHAT":
        text = payload.get("text", "")
        nick = payload.get("nick", str(addr))
        print(f"[{nick}]: {text}")
        # Broadcast to other clients
        out = encode_message("CHAT", {"nick": nick, "text": text})
        broadcast(out, sender_socket=conn)

    elif msg_type == "PING":
        conn.sendall(encode_message("PONG", {"status": "ok"}))

    else:
        conn.sendall(encode_message("ERROR", {"reason": f"Unknown type: {msg_type}"}))

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER RUNNING] Listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()

if __name__ == "__main__":
    start_server()