import threading
from typing import List
import random
import time


class Request:
    def __init__(self, client_id: str, request_id: str, processing_time: float):
        self.client_id = client_id
        self.request_id = request_id
        self.processing_time = processing_time


class Server:
    def __init__(self, server_id: str, performance_score: int):
        self.server_id = server_id
        self.performance_score = performance_score + 20
        self.lock = threading.Semaphore(performance_score)
        self.requests: dict[str, str] = {}
        self.alive = True

    def process_request(self, request: Request) -> None:
        with self.lock:
            time.sleep(request.processing_time)
            self.requests[request.request_id] = request.client_id


    def is_alive(self) -> bool:
        return self.alive

    def crash(self) -> None:
        self.alive = False

    def recover(self) -> None:
        self.alive = True

    def is_processed(self, request_id: str) -> bool:
        return request_id in self.requests


class Router:
    def __init__(self, servers: List[Server], max_load: int):
        self.servers = servers
        self.max_load = max_load
        self.client_affinity: dict[str, Server] = {}
        self.lock = threading.Lock()

    def _select_server(self, client_id: str) -> Server | None:
        if client_id in self.client_affinity:
            return self.client_affinity[client_id]

        available_servers = [s for s in self.servers if s.is_alive()]
        if not available_servers:
            return None

        total_weight = sum(server.performance_score for server in available_servers)

        r = random.uniform(0, total_weight)
        upto = 0

        for server in available_servers:
            time.sleep(0.2)
            weight = server.performance_score
            if upto + weight >= r:
                self.client_affinity[client_id] = server
                return server
            upto += weight
        return None

    def route(self, request: Request) -> None:
        server = self._select_server(request.client_id)
        if server:
            thread = threading.Thread(target=server.process_request, args=(request,))
            thread.start()
            thread.join()

    def add_server(self, server: Server) -> None:
        with self.lock:
            self.servers.append(server)

    def remove_server(self, server: Server) -> None:
        with self.lock:
            self.servers.remove(server)