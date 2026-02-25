import asyncio
from picows import ws_connect, WSFrame, WSTransport, WSListener, WSMsgType, WSCloseCode
import json
import ctypes
import dolphin_memory_engine as dme
import pickle

from util import *
from qlog import c_info
from pointers import GAME_INFO_PTR
from const import *

class ClientListener(WSListener):
    def on_ws_connected(self, transport: WSTransport):
        transport.send(WSMsgType.TEXT, b"Hello world")

    def on_ws_frame(self, transport: WSTransport, frame: WSFrame):
        print(f"Echo reply: {frame.get_payload_as_ascii_text()}")
        transport.send_close(WSCloseCode.OK)
        transport.disconnect()


async def main(url):
    transport, client = await ws_connect(ClientListener, url)

    old_info = None

    while True:
        dme.hook()

        while dme.is_hooked():
            info = c_info.from_buffer_copy(dme.read_bytes(GAME_INFO_PTR, ctypes.sizeof(c_info)))

            new_info = ctypes_to_dict(info)

            if old_info:
                diff = deep_diff(old_info, new_info)
                if len(diff):
                    for d in diff:
                        send = True
                        for path in INFO_EXCLUDE_PATHS:
                            if d.path.startswith(path):
                                send = False
                                break
                        
                        if send:
                            print(d)
                            transport.send(WSMsgType.BINARY, pickle.dumps(d.to_dict()))
            
            old_info = new_info

    await transport.wait_disconnected()


if __name__ == '__main__':
    addr = "localhost"
    port = 24436

    asyncio.run(main(f"ws://{addr}:{port}"))
