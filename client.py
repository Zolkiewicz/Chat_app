import socket
import threading
import queue
from protocol import encode_message, decode_messages, ENCODING

class Client:
    def __init__(self, host = '127.0.0.1', port = 5555):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.incoming_queue = queue.Queue()
        self.running = False

    def connect(self):
        self.sock.connect((self.host, self.port))
        self.running = True
        threading.Thread(target = self.receive_loop, daemon = True).start()

    def send(self, msg_type: str, payload: dict = None):
        if self.running:
            packet = encode_message(msg_type, payload)
            self.sock.sendall(packet)

    def receive_loop(self):
        buffer = ""
        try:
            while self.running:
                data = self.sock.recv(1024)
                if not data:
                    break
                buffer += data.decode(ENCODING)
                messages, buffer = decode_messages(buffer)
                for msg in messages:
                    self.incoming_queue.put(msg)
        except OSError:
            pass
        finally:
            self.running = False
            self.incoming_queue.put({"type": "SYSTEM", "payload": {"text": "Disconnected from server."}})

    def close(self):
        self.running = False
        self.sock.close()


def run_cli():
    client = Client()
    
    try:
        client.connect()
    except ConnectionRefusedError:
        print("Could not connect to server.")
        return

    logged_in = False
    nick = ""
    
    while client.running and not logged_in:
        nick = input("Enter your nickname: ").strip()
        if not nick:
            print("Nickname cannot be empty.")
            continue
            
        client.send("LOGIN", {"nick": nick})
        
        try:
            msg = client.incoming_queue.get(timeout=2.0)
            m_type = msg.get("type")
            payload = msg.get("payload", {})
            
            if m_type == "LOGIN_SUCCESS":
                print(f"Logged in successfully as {nick}!")
                logged_in = True
            elif m_type == "ERROR":
                print(f"Server error: {payload.get('reason', 'Unknown error')}")
            else:
                client.incoming_queue.put(msg)
        except queue.Empty:
            print("Server response timeout. Try again.")

    if not logged_in:
        client.close()
        return

    def print_incoming():
        while client.running or not client.incoming_queue.empty():
            try:
                msg = client.incoming_queue.get(timeout = 0.2)
                m_type = msg.get("type")
                payload = msg.get("payload", {})
                
                if m_type == "CHAT":
                    print(f"\r[{payload['nick']}]: {payload['text']}\n> ", end = "")
                elif m_type == "SYSTEM":
                    print(f"\r[SYSTEM]: {payload['text']}\n> ", end = "")
                elif m_type == "PONG":
                    print(f"\r[SERVER]: Pong! ({payload})\n> ", end = "")
                elif m_type == "LIST":
                    users = ", ".join(payload.get("users", []))
                    print(f"\r[ONLINE USERS]: {users}\n> ", end="")
            except queue.Empty:
                continue

    threading.Thread(target = print_incoming, daemon = True).start()

    print("Connected! Type a message or command ('/list', '/ping', '/quit').")
    try:
        while client.running:
            text = input("> ")
            if text == "/quit":
                client.close()
                break
            elif text == "/ping":
                client.send("PING")
            elif text == "/list":
                client.send("LIST")
            elif text.strip():
                client.send("CHAT", {"nick": nick, "text": text})
    except (KeyboardInterrupt, EOFError):
        print("\n[EXIT] Caught interrupt signal")
        client.close()

if __name__ == "__main__":
    run_cli()