import socket
import threading
from protocol import encode_message, decode_messages, ENCODING

HOST = '127.0.0.1'
PORT = 5555

clients = {}
clients_lock = threading.Lock()

message_history = []
history_lock = threading.Lock()
MAX_HISTORY = 50

def broadcast(message_bytes: bytes, sender_socket = None):
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
        clients[conn] = str(addr)

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            buffer += data.decode(ENCODING)
            messages, buffer = decode_messages(buffer)
            
            for msg in messages:
                process_command(conn, addr, msg)
                
    except (ConnectionResetError, OSError):
        pass
    finally:
        with clients_lock:
            if conn in clients:
                clients.pop(conn, None)
        conn.close()
        print(f"[DISCONNECTED] {addr}")

def shutdown_server(server_sock: socket.socket):
    print("\n[SHUTDOWN] Stopping server and disconnecting clients.")

    shutdown_msg = encode_message("SYSTEM", {"text": "Server is shutting down."})
    with clients_lock:
        for client in clients:
            try:
                client.sendall(shutdown_msg)
                client.shutdown(socket.SHUT_RDWR)
                client.close()
            except OSError:
                pass
        clients.clear()

    try:
        server_sock.close()
    except OSError:
        pass
    print("[SHUTDOWN] Server closed.")

def process_command(conn: socket.socket, addr, msg: dict):
    msg_type = msg.get("type")
    payload = msg.get("payload", {})
    
    if msg_type == "LOGIN":
        nick = payload.get("nick", "").strip()
        
        if not nick:
            conn.sendall(encode_message("ERROR", {"reason": "Nickname cannot be empty"}))
            return

        with clients_lock:
            if nick in clients.values():
                conn.sendall(encode_message("ERROR", {"reason": f"Nickname '{nick}' is already taken!"}))
                return
            
            clients[conn] = nick
        with clients_lock:
            clients[conn] = nick
        print(f"[LOGIN] address: {addr} nick: '{nick}'")
        conn.sendall(encode_message("LOGIN_SUCCESS", {"nick": nick}))
        with history_lock:
            if message_history:
                conn.sendall(encode_message("HISTORY", {"messages": message_history}))

        broadcast(encode_message("SYSTEM", {"text": f"{nick} connected to server."}), sender_socket=conn)
    elif msg_type == "CHAT":
        text = payload.get("text", "")
        nick = payload.get("nick", str(addr))
        print(f"[{nick}]: {text}")

        chat_data = {"nick": nick, "text": text}

        with history_lock:
            message_history.append(chat_data)
            if len(message_history) > MAX_HISTORY:
                message_history.pop(0)

        out = encode_message("CHAT", {"nick": nick, "text": text})
        broadcast(out, sender_socket=conn)

    elif msg_type == "PING":
        conn.sendall(encode_message("PONG", {"status": "ok"}))

    elif msg_type == "LIST":
        with clients_lock:
            active_users = list(clients.values())
        conn.sendall(encode_message("LIST", {"users": active_users}))

    else:
        conn.sendall(encode_message("ERROR", {"reason": f"Unknown type: {msg_type}"}))

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER RUNNING] Listening on {HOST}:{PORT}")

    try:
        while True:
            try:
                conn, addr = server.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                thread.start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        pass
    finally:
        shutdown_server(server)

if __name__ == "__main__":
    start_server()