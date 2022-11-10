import asyncio
import aiohttp
import tkinter as tk
import threading
from random import randint

from dotenv import load_dotenv
from os import getenv
from idlelib.redirector import WidgetRedirector


class Account:
    """
    The client's account.

    Handles the username and sending a message.

    Attributes
    ----------
    name: str
        The name of the client.

    """
    def __init__(self, name: str = None):
        if not name:
            name = f"Client{randint(9999, 99999)}"

        self.name = name

    def send_message(self):
        """Generate a message for the account."""
        acc_input = tk_entry_input.get()
        if not acc_input:
            return
        msg = f"{self.name}: {acc_input}\n"
        tk_entry_input.delete(0, tk.END)
        loop.create_task(session.requests.put({"chat_content": msg}))


class TextBox(tk.Text):
    """
    A read-only textbox that still allows copy-pasting.

    https://stackoverflow.com/a/11612656
    """
    def __init__(self, *args, **kwargs):
        super(TextBox, self).__init__(*args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kwargs: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kwargs: "break")


load_dotenv()

CHAT_PORT = getenv("CHAT_PORT")
HOST_URL = getenv("HOST_URL")

if "127.0.0.1" in HOST_URL or "localhost" in HOST_URL:
    ws_url = f"ws://{HOST_URL}:{CHAT_PORT}/ws"
else:
    ws_url = f"https://{HOST_URL}/ws"


class ChatSession:
    """A websocket chat session.

    Attributes
    ----------
    requests: Queue
        A queue of requests.
    """

    def __init__(self):
        self.requests = asyncio.Queue()

    async def connect(self):
        """Connect to the server."""
        async with aiohttp.ClientSession().ws_connect(ws_url) as ws:
            while True:
                while not self.requests.empty():
                    request = await self.requests.get()
                    await ws.send_json(request)
                try:
                    data = await ws.receive_json(timeout=0.5)
                    chat_content = data.get("chat_content")
                    tk_text_box.insert(tk.END, f"{chat_content}")
                except asyncio.TimeoutError:
                    pass


def generate_gui():
    """Generate the GUI."""
    font = "Whitney"
    foreground = "#eaeaea"
    chat_background = "#182128"
    input_background = "#2e434b"
    root = tk.Tk()
    text_box = TextBox(root, bg=chat_background, fg=foreground, font=font, width=60)
    text_box.grid(row=0, column=0, columnspan=32)
    scroll_bar = tk.Scrollbar(text_box)

    entry_field = tk.Entry(root, bg=input_background, fg=foreground, font=font, width=55)
    entry_field.grid(row=16, column=0)
    entry_field.focus()

    send = tk.Button(root, text="Send", font=font, bg=chat_background, command=account.send_message, width=5)
    send.grid(row=16, column=4)
    entry_field.bind('<Return>', lambda event: account.send_message())

    return root, text_box, entry_field, send


def start_asyncio_thread():
    """Start the asyncio thread that handles the websocket."""
    loop.create_task(session.connect())
    loop.run_forever()


if __name__ == '__main__':
    try:
        account = Account()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        session = ChatSession()
        thread = threading.Thread(target=start_asyncio_thread).start()
        tk_root, tk_text_box, tk_entry_input, tk_send = generate_gui()
        tk_root.title(f"Chat App - {account.name}")
        tk_root.mainloop()
    except KeyboardInterrupt:
        ...
