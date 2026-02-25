import asyncio
from picows import ws_create_server, WSFrame, WSTransport, WSListener, WSMsgType, WSUpgradeRequest
import pickle

import yaml

from const import *

with open("multitp_config.yml") as stream:
    try:
        CONFIG = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print("Failed to load config:", exc)


class Room():
    admin: "ClientListener"
    clients: list["ClientListener"]
    code: str

    def __init__(self, code: str, admin: "ClientListener"):
        self.code = code
        self.admin = admin
        self.add_client(admin)
    
    def add_client(self, client: "ClientListener"):
        self.clients.append(client)
        client.room = self

class ClientListener(WSListener):
    room: Room

    def on_ws_connected(self, transport: WSTransport):
        print(f"New connection from {transport.underlying_transport.get_extra_info('peername')}")

    def on_ws_frame(self, transport: WSTransport, frame: WSFrame):
        if frame.msg_type == WSMsgType.CLOSE:
            transport.send_close(frame.get_close_code(), frame.get_close_message())
            transport.disconnect()
        elif frame.msg_type == WSMsgType.BINARY:
            d = pickle.loads(frame.get_payload_as_bytes())
            print(transport.underlying_transport.get_extra_info('peername'), d)

async def main():
    def listener_factory(r: WSUpgradeRequest):
        return ClientListener()

    server: asyncio.Server = await ws_create_server(
        listener_factory,
        CONFIG.get("server").get("ip"),
        CONFIG.get("server").get("port")
    )
    
    for s in server.sockets:
        print(f"Server started on {s.getsockname()}")

    await server.serve_forever()

if __name__ == '__main__':
  asyncio.run(main())
