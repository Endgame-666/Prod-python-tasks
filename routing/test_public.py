import pytest
import threading
import time
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from routing import Router, Server, Request

@pytest.fixture
def servers():
    return [
        Server("server1", 100),
        Server("server2", 150),
        Server("server3", 200),
    ]

@pytest.fixture
def router(servers):
    return Router(servers, max_load=5)


def test_server_process_request():
    server = Server("test_server", 100)
    request = Request("client1", "request1", 0.1)

    server.process_request(request)
    assert server.is_processed("request1")
    assert not server.is_processed("request2")

def test_server_crash_and_recover():
    server = Server("test_server", 100)
    assert server.is_alive()

    server.crash()
    assert not server.is_alive()

    server.recover()
    assert server.is_alive()

def test_router_basic_routing(router):
    request = Request("client1", "request1", 0.1)
    router.route(request)

    assert any(server.is_processed("request1") for server in router.servers)

def test_router_round_robin(router):
    num_requests = 1000
    for server in router.servers:
        server.performance_score = 100  # Set a uniform performance score

    requests = [Request(f"client{i}", f"request{i}", 0.01) for i in range(num_requests)]

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(router.route, request) for request in requests]
        for future in futures:
            future.result()

    processed_counts = [sum(server.is_processed(f"request{i}") for i in range(num_requests)) for server in router.servers]
    print('\n')
    print(processed_counts)
    # Check that the processed counts are within a reasonable range of each other
    assert max(processed_counts) - min(processed_counts) <= num_requests * 0.05  # Allow for some deviation due to concurrency


def test_router_max_load(router):
    slow_request_time = 0.2
    num_requests = 7
    num_servers = len(router.servers)
    max_load = router.max_load

    processed_requests = []

    def slow_request(index: int):
        request = Request(f"client_slow_{index}", f"request_slow_{index}", slow_request_time)
        router.route(request)
        processed_requests.append(request)

    start_time = time.time()
    threads = [threading.Thread(target=slow_request, args=(i,)) for i in range(num_requests)]
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    end_time = time.time()
    total_time = end_time - start_time
    # All requests should be processed now
    assert len(processed_requests) == num_requests, f"Processed requests: {len(processed_requests)}"

    min_expected_time = slow_request_time * (num_requests // min(num_servers, max_load) + 1)
    max_expected_time = slow_request_time * (num_requests // min(num_servers, max_load) + 1) * 2

    assert total_time >= min_expected_time, f"Total time ({total_time:.2f}s) is less than expected minimum ({min_expected_time:.2f}s)"
    assert total_time <= max_expected_time, f"Total time ({total_time:.2f}s) exceeds expected maximum ({max_expected_time:.2f}s)"


def test_router_server_failure(router):
    router.servers[0].crash()

    requests = [Request(f"client{i}", f"request{i}", 0.1) for i in range(6)]
    for request in requests:
        router.route(request)

    assert not any(router.servers[0].is_processed(f"request{i}") for i in range(6))
    assert all(any(server.is_processed(f"request{i}") for server in router.servers[1:]) for i in range(6))


def test_router_add_remove_server(router):
    new_server = Server("new_server", 175)
    router.add_server(new_server)
    assert new_server.server_id in set(server.server_id for server in router.servers)

    some_server = router.servers[0]
    router.remove_server(some_server)
    assert some_server.server_id not in set(server.server_id for server in router.servers)


def test_concurrent_requests(router):
    def make_request(client_id: str, request_id: str):
        request = Request(client_id, request_id, 0.1)
        router.route(request)
        return request_id

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, f"client{i}", f"request{i}") for i in range(20)]
        results = [future.result() for future in as_completed(futures)]

    assert len(results) == 20
    assert all(any(server.is_processed(request_id) for server in router.servers) for request_id in results)


def test_weighted_round_robin(servers):
    weighted_router = Router(servers, max_load=10)
    requests = [Request(f"client{i}", f"request{i}", 0.1) for i in range(90)]

    def route_request(request):
        weighted_router.route(request)
        return request.request_id

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(route_request, request) for request in requests]
        results = [future.result() for future in as_completed(futures)]

    assert len(results) == 90

    processed_counts = [sum(server.is_processed(f"request{i}") for i in range(90)) for server in weighted_router.servers]
    total_weight = sum(server.performance_score for server in servers)
    expected_ratios = [server.performance_score / total_weight for server in servers]

    for count, expected_ratio in zip(processed_counts, expected_ratios):
        assert abs(count / 90 - expected_ratio) < 0.1  # Allow for some deviation due to concurrency


def test_client_affinity(router):
    client_requests = {f"client{i}": [Request(f"client{i}", f"request{i}_{j}", 0.1) for j in range(5)] for i in range(3)}

    def route_client_requests(client, requests):
        for request in requests:
            router.route(request)
        return client

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(route_client_requests, client, requests) for client, requests in client_requests.items()]
        results = [future.result() for future in as_completed(futures)]

    assert len(results) == 3

    for client, requests in client_requests.items():
        processed_servers = [server for server in router.servers if any(server.is_processed(request.request_id) for request in requests)]
        assert len(processed_servers) == 1  # All requests from one client should be processed by the same server