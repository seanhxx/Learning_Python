from channels.routing import route
from tools.consumers import ws_connect, ws_keepalive, ws_message, ws_disconnect

channel_routing = [
    route("websocket.connect", ws_connect),
    route("websocket.receive", ws_message),
    route("websocket.keepalive", ws_keepalive),
    route("websocket.disconnect", ws_disconnect),
]