from jlib.ws.manager import WSManager

_DEFAULT_WS_MANAGER = WSManager()


def get_ws_manager():
    return _DEFAULT_WS_MANAGER
