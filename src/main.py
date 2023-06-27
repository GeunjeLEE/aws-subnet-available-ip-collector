from prometheus_client import start_http_server, CollectorRegistry, Gauge
from manager.subnet_ip_counter_manager import SubnetIpCounterManager
import time

registry = CollectorRegistry()
subnet_mgr = SubnetIpCounterManager()


def run():
    print("start server...")
    start_http_server(8000)

    g = Gauge('available_ip_count', 'available ip count by subnet',
              labelnames=['collect_from', 'vpc_id', 'subnet_id'],
              registry=registry)

    while True:
        subnet_mgr.collect_subnet_available_ips(g)
        subnet_mgr.push_gateway(registry)
        time.sleep(5)


if __name__ == '__main__':
    run()
