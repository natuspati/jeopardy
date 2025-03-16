from threading import Thread

from fakeredis import TcpFakeServer

from settings import settings


def start_redis_server():
    server_address = (settings.redis_host, settings.redis_port)
    server = TcpFakeServer(server_address, server_type="redis")
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()
