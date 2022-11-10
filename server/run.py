import asyncio

from dotenv import load_dotenv
from hypercorn.config import Config
from hypercorn.asyncio import serve
from os import getenv
from quart_openapi import Pint
import ws

load_dotenv()

CHAT_PORT = getenv("CHAT_PORT")
app = Pint(__name__, title="ChatApp", version="0.1")
app.register_blueprint(ws.ws_blueprint)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    config = Config()
    config.bind = f"127.0.0.1:{CHAT_PORT}"
    loop.run_until_complete(serve(app, config))
