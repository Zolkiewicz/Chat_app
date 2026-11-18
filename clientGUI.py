import tkinter as tk
from protocol import encode_message, decode_messages, ENCODING
from client import Client

class ChatApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Chat")
        self.root.geometry("800x800")
        self.root.configure(bg="#D34F76")

        try:
            self.root.iconbitmap("info")
        except tk.TclError:
            pass

        self.client = Client()
        self.logged_in = False
        self.nick = ""

        self.entry = tk.Entry(root, bg="#30223B", fg="#D34F76")
        self.entry.pack(side=tk.BOTTOM, padx=5, pady=5, fill=tk.X)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.text_area = tk.Text(root, state="disabled", wrap=tk.WORD, bg="#241F31", fg="#c1381d")
        self.text_area.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.text_area.tag_config("my_msg", foreground="#D34F76")

        try:
            self.client.connect()
            self.write_line("Enter your nickname:")
        except ConnectionRefusedError:
            self.write_line("Could not connect to server.")

        self.root.after(50, self.check_queue)

    def write_line(self, text: str, tag: str = None):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, text + "\n", tag)
        self.text_area.see(tk.END)
        self.text_area.config(state="disabled")

    def on_enter(self, event=None):
        text = self.entry.get()
        self.entry.delete(0, tk.END)

        if not self.client.running:
            return

        if not self.logged_in:
            nick = text.strip()
            if not nick:
                self.write_line("Nickname cannot be empty.")
                return
            self.nick = nick
            self.client.send("LOGIN", {"nick": nick})
            return

        if text == "/quit":
            self.on_close()
        elif text == "/ping":
            self.client.send("PING")
        elif text == "/list":
            self.client.send("LIST")
        elif text.strip():
            self.write_line(f"[{self.nick}]: {text}", "my_msg")
            self.client.send("CHAT", {"nick": self.nick, "text": text})

    def check_queue(self):
        while not self.client.incoming_queue.empty():
            msg = self.client.incoming_queue.get()
            m_type = msg.get("type")
            payload = msg.get("payload", {})

            if m_type == "LOGIN_SUCCESS":
                self.logged_in = True
                self.write_line(f"Logged in successfully as {self.nick}!")
            elif m_type == "HISTORY":
                for past in payload.get("messages", []):
                    self.write_line(f"[{past['nick']}]: {past['text']}")
                self.write_line("Connected! Type a message or command ('/list', '/ping', '/quit').")
            elif m_type == "ERROR":
                self.write_line(f"Server error: {payload.get('reason', 'Unknown error')}")
                if not self.logged_in:
                    self.write_line("Enter your nickname:")
            elif m_type == "CHAT":
                self.write_line(f"[{payload['nick']}]: {payload['text']}")
            elif m_type == "SYSTEM":
                self.write_line(f"[SYSTEM]: {payload['text']}")
            elif m_type == "PONG":
                self.write_line(f"[SERVER]: Pong! ({payload})")
            elif m_type == "LIST":
                users = ", ".join(payload.get("users", []))
                self.write_line(f"[ONLINE USERS]: {users}")

        self.root.after(50, self.check_queue)

    def on_close(self):
        self.client.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()