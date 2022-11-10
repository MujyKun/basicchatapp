import asyncio
from typing import Dict

from quart import Blueprint, websocket
from random import randint

ws_blueprint = Blueprint("ws", __name__)


class Session:
    """A session

    Parameters
    ----------
    s_id: int
        A unique session ID.
    queue: Queue
        A queue to hold requests that need to be sent to the session.
    """
    def __init__(self, s_id):
        self.id = s_id
        self.queue = asyncio.Queue()


@ws_blueprint.websocket("/ws")
async def ws():
    """Create a WebSocket connection and handle chat requests/responses."""
    await websocket.accept()
    min_int = 9999
    max_int = 99999
    s_id = randint(min_int, max_int)
    while s_id in sessions.keys():
        s_id = randint(min_int, max_int)

    session = Session(s_id)
    sessions[s_id] = session
    try:
        while True:
            while not session.queue.empty():
                data = await session.queue.get()
                await websocket.send_json(data)

            try:
                data = await asyncio.wait_for(websocket.receive_json(), 0.5)
            except asyncio.TimeoutError:
                continue

            for t_session in sessions.values():
                await t_session.queue.put(data)
    except Exception as e:
        print(e)

    sessions.pop(s_id)


sessions: Dict[int, Session] = dict()
